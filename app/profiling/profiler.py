import pandas as pd


def profile_dataset(
    df: pd.DataFrame,
) -> dict:

    numeric_columns = df.select_dtypes(
        include="number"
    ).columns.tolist()

    categorical_columns = df.select_dtypes(
        exclude="number"
    ).columns.tolist()

    return {

        "rows": len(df),

        "columns": len(df.columns),

        "column_names": df.columns.tolist(),

        "numeric_columns": numeric_columns,

        "categorical_columns": categorical_columns,

        "missing_values": (
            df.isna()
              .sum()
              .to_dict()
        ),

        "duplicate_rows": int(
            df.duplicated().sum()
        ),
    }