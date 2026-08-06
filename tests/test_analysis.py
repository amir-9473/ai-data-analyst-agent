import pandas as pd
import pytest

from app.tools.analysis import analyze_data, dataset_overview, resolve_column


@pytest.fixture
def frame():
    return pd.DataFrame(
        {
            "Age": [20, 25, 30, 80],
            "Blood Pressure": [110, 120, 125, 190],
            "گروه": ["الف", "الف", "ب", "ب"],
        }
    )


def test_resolves_case_typo_and_semantic_aliases(frame):
    assert resolve_column(frame, "age") == "Age"
    assert resolve_column(frame, "ag") == "Age"
    assert resolve_column(frame, "سن") == "Age"
    assert resolve_column(frame, "فشار خون") == "Blood Pressure"


@pytest.mark.parametrize("method", ["describe", "missing", "correlation", "outliers", "frequency"])
def test_analysis_methods_return_json_friendly_results(frame, method):
    result = analyze_data(frame, method)
    assert result["method"] == method
    assert "result" in result


def test_group_and_trend_analysis(frame):
    grouped = analyze_data(frame, "group", ["سن"], group_by="گروه")
    trend = analyze_data(frame, "trend", ["سن", "فشار خون"])

    assert grouped["group_by"] == "گروه"
    assert trend["x"] == "Age"
    assert trend["pearson_correlation"] > 0
    assert dataset_overview(frame)["rows"] == 4
