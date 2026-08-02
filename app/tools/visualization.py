from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


CHART_DIR = Path("outputs/charts")


def create_histogram(
    df: pd.DataFrame,
    column: str,
) -> str:

    if column not in df.columns:

        raise ValueError(
            f"Column '{column}' not found."
        )

    if not pd.api.types.is_numeric_dtype(
        df[column]
    ):

        raise ValueError(
            "Histogram requires "
            "a numeric column."
        )

    CHART_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    output_path = (
        CHART_DIR
        / f"{column}_histogram.png"
    )

    plt.figure()

    plt.hist(
        df[column].dropna()
    )

    plt.title(
        f"Distribution of {column}"
    )

    plt.xlabel(
        column
    )

    plt.ylabel(
        "Frequency"
    )

    plt.savefig(
        output_path
    )

    plt.close()

    return str(
        output_path
    )