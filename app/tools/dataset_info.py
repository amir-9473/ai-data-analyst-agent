# ==========================================================
# Dataset Information Tools
# ==========================================================

import pandas as pd


# ==========================================================
# List Columns
# ==========================================================

def list_columns(
    df: pd.DataFrame,
) -> dict:

    """
    Return dataset column names.
    """

    return {

        "columns": (
            df.columns.tolist()
        )

    }


# ==========================================================
# Dataset Overview
# ==========================================================

def dataset_overview(
    df: pd.DataFrame,
) -> dict:

    """
    Return basic dataset information.
    """

    return {

        "rows": (
            len(df)
        ),

        "columns": (
            len(df.columns)
        ),

    }


# ==========================================================
# Column Information
# ==========================================================

def column_information(
    df: pd.DataFrame,
    column_name: str,
) -> dict:

    """
    Return information about one column.
    """

    if column_name not in df.columns:

        return {

            "error": (
                f"Column "
                f"{column_name} "
                "not found."
            )

        }


    column = df[column_name]


    return {

        "column": column_name,

        "dtype": (
            str(column.dtype)
        ),

        "missing_values": (
            int(
                column.isna()
                .sum()
            )
        ),

        "unique_values": (
            int(
                column.nunique()
            )
        ),

    }