import pandas as pd


def calculate_statistics(
    df: pd.DataFrame,
) -> dict:

    numeric_df = df.select_dtypes(
        include="number"
    )

    if numeric_df.empty:
        return {
            "message": "No numeric columns found."
        }

    statistics = (
        numeric_df
        .describe()
        .round(2)
        .to_dict()
    )

    return statistics