import pandas as pd


def calculate_correlation(
    df: pd.DataFrame,
) -> dict:

    numeric_df = df.select_dtypes(
        include="number"
    )

    if numeric_df.shape[1] < 2:

        return {
            "message": (
                "At least two numeric "
                "columns are required."
            )
        }

    correlation = (
        numeric_df
        .corr()
        .round(2)
        .to_dict()
    )

    return correlation