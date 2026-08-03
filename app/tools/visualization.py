# ==========================================================
# Visualization Tool
# ==========================================================

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


# ==========================================================
# Project Paths
# ==========================================================

PROJECT_ROOT = Path(
    __file__
).resolve().parents[2]


OUTPUT_DIR = (
    PROJECT_ROOT
    / "outputs"
    / "charts"
)


# ==========================================================
# Create Output Directory
# ==========================================================

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# ==========================================================
# Create Histogram
# ==========================================================

def create_histogram(
    df: pd.DataFrame,
    column_name: str,
) -> str:

    """
    Create a histogram for a numeric column.

    Parameters
    ----------
    df:
        Input pandas DataFrame.

    column_name:
        Name of the numeric column.

    Returns
    -------
    str
        Path to the generated chart.
    """

    # ------------------------------------------------------
    # Validate Column
    # ------------------------------------------------------

    if column_name not in df.columns:

        raise ValueError(
            f"Column '{column_name}' "
            "does not exist."
        )


    # ------------------------------------------------------
    # Validate Numeric Column
    # ------------------------------------------------------

    if not pd.api.types.is_numeric_dtype(
        df[column_name]
    ):

        raise ValueError(
            f"Column '{column_name}' "
            "is not numeric."
        )


    # ------------------------------------------------------
    # Output File Path
    # ------------------------------------------------------

    file_path = (

        OUTPUT_DIR

        / (
            f"histogram_"
            f"{column_name}.png"
        )

    )


    # ------------------------------------------------------
    # Create Figure
    # ------------------------------------------------------

    plt.figure(
        figsize=(
            8,
            5,
        )
    )


    # ------------------------------------------------------
    # Create Histogram
    # ------------------------------------------------------

    plt.hist(
        df[column_name].dropna()
    )


    # ------------------------------------------------------
    # Chart Labels
    # ------------------------------------------------------

    plt.title(
        f"Distribution of "
        f"{column_name}"
    )

    plt.xlabel(
        column_name
    )

    plt.ylabel(
        "Frequency"
    )


    # ------------------------------------------------------
    # Layout
    # ------------------------------------------------------

    plt.tight_layout()


    # ------------------------------------------------------
    # Save Chart
    # ------------------------------------------------------

    plt.savefig(
        file_path
    )


    # ------------------------------------------------------
    # Close Figure
    # ------------------------------------------------------

    plt.close()


    # ------------------------------------------------------
    # Return File Path
    # ------------------------------------------------------

    return str(
        file_path
    )