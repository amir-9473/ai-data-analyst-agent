from pathlib import Path

import pandas as pd
import pytest

import app.tools.visualization as visualization


@pytest.fixture
def frame():
    return pd.DataFrame(
        {
            "سن": [20, 25, 30, 35, 40],
            "حقوق": [10, 14, 15, 20, 22],
            "گروه": ["الف", "الف", "ب", "ب", "ب"],
        }
    )


@pytest.mark.parametrize(
    ("chart_type", "arguments"),
    [
        ("histogram", {"x": "سن"}),
        ("box", {"x": "سن", "group_by": "گروه"}),
        ("scatter", {"x": "سن", "y": "حقوق"}),
        ("line", {"x": "سن", "y": "حقوق"}),
        ("bar", {"x": "گروه", "y": "حقوق"}),
        ("pie", {"x": "گروه"}),
        ("correlation", {}),
    ],
)
def test_all_chart_types(tmp_path, monkeypatch, frame, chart_type, arguments):
    monkeypatch.setattr(visualization, "CHART_DIR", tmp_path)
    result = visualization.create_chart(frame, chart_type, **arguments)

    assert result["chart_type"] == chart_type
    assert Path(result["path"]).is_file()


def test_vazirmatn_font_is_available_for_chart_labels():
    assert visualization.FONT_PATH.is_file()
    assert visualization.FONT_FAMILY == "Vazirmatn"
