"""Reusable charts with safe column matching and Persian label support."""

import re
from pathlib import Path
from uuid import uuid4

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import font_manager

from app.tools.analysis import resolve_column


CHART_DIR = Path(__file__).resolve().parents[2] / "outputs" / "charts"
FONT_PATH = Path(__file__).resolve().parents[2] / "assets" / "fonts" / "Vazirmatn-Regular.ttf"
if FONT_PATH.exists():
    font_manager.fontManager.addfont(FONT_PATH)
    FONT_FAMILY = font_manager.FontProperties(fname=FONT_PATH).get_name()
else:  # pragma: no cover - the bundled font is expected in packaged builds
    FONT_FAMILY = "DejaVu Sans"


def _display(text: object) -> str:
    value = str(text)
    if not re.search(r"[\u0600-\u06ff]", value):
        return value
    try:
        import arabic_reshaper
        from bidi.algorithm import get_display

        return get_display(arabic_reshaper.reshape(value))
    except ImportError:
        return value


def _label(axis, *, title: str, x: str = "", y: str = "") -> None:
    axis.set_title(_display(title))
    axis.set_xlabel(_display(x))
    axis.set_ylabel(_display(y))


def _apply_font(axis) -> None:
    # Matplotlib needs an explicit Arabic-capable font for Persian labels.
    texts = [axis.title, axis.xaxis.label, axis.yaxis.label, *axis.get_xticklabels(), *axis.get_yticklabels(), *axis.texts]
    if legend := axis.get_legend():
        texts.extend([legend.get_title(), *legend.get_texts()])
    for text in texts:
        text.set_fontfamily(FONT_FAMILY)


def create_chart(
    df: pd.DataFrame,
    chart_type: str,
    x: str | None = None,
    y: str | None = None,
    group_by: str | None = None,
) -> dict:
    """Create one of: histogram, box, scatter, line, bar, pie or correlation."""
    chart_type = chart_type.casefold().strip()
    if chart_type not in {"histogram", "box", "scatter", "line", "bar", "pie", "correlation"}:
        raise ValueError(f"Unknown chart type: {chart_type}")

    group = resolve_column(df, group_by) if group_by else None
    if chart_type == "correlation":
        columns = list(df.select_dtypes("number").columns)
        if len(columns) < 2:
            raise ValueError("A correlation chart needs at least two numeric columns.")
        resolved_x = resolved_y = None
    else:
        if not x:
            raise ValueError(f"{chart_type} chart needs an x column.")
        resolved_x = resolve_column(df, x, numeric=chart_type in {"histogram", "box", "scatter", "line"})
        resolved_y = resolve_column(df, y, numeric=True) if y else None

    figure, axis = plt.subplots(figsize=(8, 5))
    title: str

    if chart_type == "histogram":
        axis.hist(df[resolved_x].dropna(), bins="auto", color="#2563eb", edgecolor="white")
        title = f"Distribution of {resolved_x}"
        _label(axis, title=title, x=resolved_x, y="Frequency")

    elif chart_type == "box":
        if group:
            grouped = [(name, values[resolved_x].dropna()) for name, values in df.groupby(group, dropna=False, observed=True)]
            axis.boxplot([values for _, values in grouped], tick_labels=[_display(name) for name, _ in grouped])
            title = f"{resolved_x} by {group}"
            _label(axis, title=title, x=group, y=resolved_x)
        else:
            axis.boxplot(df[resolved_x].dropna(), tick_labels=[_display(resolved_x)])
            title = f"Box plot of {resolved_x}"
            _label(axis, title=title, y=resolved_x)

    elif chart_type in {"scatter", "line"}:
        if not resolved_y:
            raise ValueError(f"{chart_type} chart needs a y column.")
        clean = df[[resolved_x, resolved_y] + ([group] if group else [])].dropna()
        if chart_type == "scatter":
            if group:
                for name, values in clean.groupby(group, observed=True):
                    axis.scatter(values[resolved_x], values[resolved_y], alpha=0.7, label=_display(name))
                axis.legend(title=_display(group))
            else:
                axis.scatter(clean[resolved_x], clean[resolved_y], alpha=0.7, color="#2563eb")
        else:
            clean = clean.sort_values(resolved_x)
            axis.plot(clean[resolved_x], clean[resolved_y], marker="o", linewidth=1.5, color="#2563eb")
        title = f"{resolved_y} vs {resolved_x}"
        _label(axis, title=title, x=resolved_x, y=resolved_y)

    elif chart_type == "bar":
        if resolved_y:
            values = df.groupby(resolved_x, dropna=False, observed=True)[resolved_y].mean().sort_values(ascending=False).head(20)
            y_label = f"Mean {resolved_y}"
        else:
            values = df[resolved_x].value_counts(dropna=False).head(20)
            y_label = "Count"
        labels = [_display(value) for value in values.index]
        axis.bar(labels, values.values, color="#2563eb")
        axis.tick_params(axis="x", rotation=35)
        title = f"{resolved_y + ' by ' if resolved_y else ''}{resolved_x}"
        _label(axis, title=title, x=resolved_x, y=y_label)

    elif chart_type == "pie":
        values = df[resolved_x].value_counts(dropna=False).head(10)
        axis.pie(values.values, labels=[_display(value) for value in values.index], autopct="%1.1f%%")
        title = f"Share of {resolved_x}"
        axis.set_title(_display(title))

    else:
        correlation = df.select_dtypes("number").corr()
        image = axis.imshow(correlation, cmap="coolwarm", vmin=-1, vmax=1)
        labels = [_display(column) for column in correlation.columns]
        axis.set_xticks(np.arange(len(labels)), labels=labels, rotation=45, ha="right")
        axis.set_yticks(np.arange(len(labels)), labels=labels)
        figure.colorbar(image, ax=axis, label="Correlation")
        title = "Correlation heatmap"
        axis.set_title(title)

    if chart_type not in {"pie", "correlation"}:
        axis.grid(alpha=0.18)
    _apply_font(axis)
    figure.tight_layout()
    CHART_DIR.mkdir(parents=True, exist_ok=True)
    path = CHART_DIR / f"{chart_type}_{uuid4().hex[:10]}.png"
    figure.savefig(path, dpi=130, bbox_inches="tight")
    plt.close(figure)
    return {
        "type": "chart",
        "chart_type": chart_type,
        "title": title,
        "path": str(path),
        "columns": [name for name in (resolved_x, resolved_y, group) if name],
    }
