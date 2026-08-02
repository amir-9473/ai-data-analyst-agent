import pandas as pd


def analyze_missing_values(
    df: pd.DataFrame,
) -> dict:

    missing_counts = (
        df.isna()
        .sum()
    )

    missing_percentages = (
        df.isna()
        .mean()
        .mul(100)
        .round(2)
    )

    result = {}

    for column in df.columns:

        result[column] = {
            "count": int(
                missing_counts[column]
            ),
            "percentage": float(
                missing_percentages[column]
            ),
        }

    return result