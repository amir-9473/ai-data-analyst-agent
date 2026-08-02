# ==========================================================
# Analysis Service
# ==========================================================

from app.llm.client import (
    generate_answer,
)


# ==========================================================
# Generate Analysis Summary
# ==========================================================

def generate_analysis_summary(
    statistics: dict,
    missing_values: dict,
    correlation: dict,
) -> str:

    prompt = f"""
You are a professional data analyst.

Analyze the following dataset analysis results.

Statistics:
{statistics}

Missing Values:
{missing_values}

Correlation:
{correlation}

Provide a concise and clear summary.

Mention:

1. Important numerical statistics.
2. Significant missing values.
3. Important correlations.
4. Notable data quality issues.

Do not invent information that is not
present in the provided results.
"""

    return generate_answer(
        prompt
    )