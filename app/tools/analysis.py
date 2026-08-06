"""Small, JSON-friendly data analysis toolkit used by the agent."""

import json
import re
import unicodedata
from difflib import SequenceMatcher

import numpy as np
import pandas as pd


ALIASES = {
    "age": ("age", "سن", "سن و سال"),
    "bloodpressure": ("blood pressure", "pressure", "فشار خون", "فشار"),
    "bmi": ("bmi", "body mass index", "شاخص توده بدنی", "توده بدنی"),
    "glucose": ("glucose", "blood sugar", "قند", "قند خون", "گلوکز"),
    "income": ("income", "salary", "wage", "درآمد", "حقوق"),
    "weight": ("weight", "وزن"),
    "height": ("height", "قد"),
    "gender": ("gender", "sex", "جنسیت"),
    "outcome": ("outcome", "target", "label", "نتیجه", "خروجی"),
}


def _normalize(value: object) -> str:
    text = unicodedata.normalize("NFKC", str(value)).casefold()
    text = text.translate(str.maketrans({"ي": "ی", "ك": "ک", "ۀ": "ه"}))
    return re.sub(r"[^\w]+", "", text, flags=re.UNICODE)


def resolve_column(
    df: pd.DataFrame,
    requested: str,
    *,
    numeric: bool = False,
) -> str:
    """Resolve case, spacing, typo and common Persian/English column aliases."""
    candidates = list(df.select_dtypes("number").columns if numeric else df.columns)
    if not requested or not candidates:
        raise ValueError("No suitable column was provided or found.")

    query = _normalize(requested)
    normalized = {_normalize(column): str(column) for column in candidates}
    if query in normalized:
        return normalized[query]

    for canonical, aliases in ALIASES.items():
        family = {_normalize(alias) for alias in aliases} | {_normalize(canonical)}
        if query in family:
            for name, original in normalized.items():
                if name in family:
                    return original

    partial = [original for name, original in normalized.items() if query in name or name in query]
    if len(partial) == 1:
        return partial[0]

    scores = sorted(
        ((SequenceMatcher(None, query, name).ratio(), original) for name, original in normalized.items()),
        reverse=True,
    )
    if scores and scores[0][0] >= 0.58:
        return scores[0][1]

    choices = ", ".join(map(str, candidates[:12]))
    raise ValueError(f"Column '{requested}' is ambiguous or unavailable. Available: {choices}")


def _columns(df: pd.DataFrame, names: list[str] | str | None, *, numeric: bool = False) -> list[str]:
    if isinstance(names, str):
        names = [names]
    if names:
        return list(dict.fromkeys(resolve_column(df, name, numeric=numeric) for name in names))
    return list(df.select_dtypes("number").columns if numeric else df.columns)


def _records(frame: pd.DataFrame) -> list[dict]:
    return json.loads(frame.to_json(orient="records", force_ascii=False, date_format="iso"))


def dataset_overview(df: pd.DataFrame) -> dict:
    columns = pd.DataFrame(
        {
            "column": df.columns.astype(str),
            "type": df.dtypes.astype(str).values,
            "missing_percent": (df.isna().mean().mul(100).round(2)).values,
            "unique": df.nunique(dropna=True).values,
        }
    )
    return {
        "rows": len(df),
        "columns": len(df.columns),
        "duplicate_rows": int(df.duplicated().sum()),
        "schema": _records(columns),
    }


def analyze_data(
    df: pd.DataFrame,
    method: str,
    columns: list[str] | str | None = None,
    group_by: str | None = None,
    correlation_method: str = "pearson",
) -> dict:
    """Run a descriptive, quality, correlation, grouping, outlier or trend analysis."""
    method = method.casefold().strip()

    if method == "describe":
        selected = _columns(df, columns, numeric=True)
        result = df[selected].describe().T
        result["median"] = df[selected].median()
        result["missing"] = df[selected].isna().sum()
        result["skew"] = df[selected].skew()
        result = result.round(3).reset_index(names="column")
        return {"method": method, "result": _records(result)}

    if method == "missing":
        selected = _columns(df, columns)
        result = pd.DataFrame(
            {
                "column": selected,
                "missing": [int(df[name].isna().sum()) for name in selected],
                "missing_percent": [round(float(df[name].isna().mean() * 100), 2) for name in selected],
            }
        ).sort_values("missing", ascending=False)
        return {"method": method, "duplicate_rows": int(df.duplicated().sum()), "result": _records(result)}

    if method == "correlation":
        selected = _columns(df, columns, numeric=True)
        if len(selected) < 2:
            raise ValueError("Correlation needs at least two numeric columns.")
        correlation_method = correlation_method if correlation_method in {"pearson", "spearman", "kendall"} else "pearson"
        matrix = df[selected].corr(method=correlation_method).round(3)
        return {
            "method": method,
            "correlation_method": correlation_method,
            "result": json.loads(matrix.to_json(force_ascii=False)),
        }

    if method == "outliers":
        selected = _columns(df, columns, numeric=True)
        rows = []
        for name in selected:
            series = df[name].dropna()
            q1, q3 = series.quantile([0.25, 0.75])
            iqr = q3 - q1
            mask = (series < q1 - 1.5 * iqr) | (series > q3 + 1.5 * iqr)
            rows.append(
                {
                    "column": name,
                    "count": int(mask.sum()),
                    "percent": round(float(mask.mean() * 100), 2),
                    "lower_bound": round(float(q1 - 1.5 * iqr), 3),
                    "upper_bound": round(float(q3 + 1.5 * iqr), 3),
                }
            )
        return {"method": method, "rule": "1.5 × IQR", "result": rows}

    if method == "frequency":
        selected = _columns(df, columns)
        result = {
            name: {str(key): int(value) for key, value in df[name].value_counts(dropna=False).head(12).items()}
            for name in selected
        }
        return {"method": method, "result": result}

    if method == "group":
        if not group_by:
            raise ValueError("Grouped analysis needs group_by.")
        group = resolve_column(df, group_by)
        selected = [name for name in _columns(df, columns, numeric=True) if name != group]
        if not selected:
            raise ValueError("Grouped analysis needs at least one numeric value column.")
        result = df.groupby(group, dropna=False, observed=True)[selected].agg(["count", "mean", "median", "min", "max"])
        result.columns = [f"{column}_{metric}" for column, metric in result.columns]
        return {"method": method, "group_by": group, "result": _records(result.round(3).reset_index())[:100]}

    if method == "trend":
        selected = _columns(df, columns, numeric=True)
        if len(selected) != 2:
            raise ValueError("Trend analysis needs exactly two numeric columns.")
        clean = df[selected].dropna()
        if len(clean) < 2:
            raise ValueError("Trend analysis needs at least two complete rows.")
        x, y = selected
        slope, intercept = np.polyfit(clean[x], clean[y], 1)
        return {
            "method": method,
            "x": x,
            "y": y,
            "rows_used": len(clean),
            "pearson_correlation": round(float(clean[x].corr(clean[y])), 3),
            "linear_slope": round(float(slope), 3),
            "linear_intercept": round(float(intercept), 3),
        }

    raise ValueError(f"Unknown analysis method: {method}")
