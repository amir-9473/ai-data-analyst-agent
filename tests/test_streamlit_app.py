from pathlib import Path

import pandas as pd
from streamlit.testing.v1 import AppTest

from app.schemas.agent_schema import AgentResponse


def test_streamlit_demo_starts():
    app = AppTest.from_file("streamlit_app.py").run(timeout=20)
    assert not app.exception
    assert app.title[0].value == "AI Data Analyst"
    assert "unicode-bidi: plaintext" in app.markdown[0].value


def test_streamlit_demo_accepts_the_persian_sample():
    path = next(Path("uploads").glob("1b39*.csv"))
    app = AppTest.from_file("streamlit_app.py").run(timeout=20)
    app.file_uploader[0].upload(path.name, path.read_bytes(), "text/csv").run(timeout=20)

    assert not app.exception
    assert [metric.value for metric in app.metric] == ["31", "10", "186", "0"]
    assert app.text_area


def test_streamlit_demo_uses_bidirectional_result_renderer():
    app = AppTest.from_file("streamlit_app.py")
    app.session_state["dataset"] = pd.DataFrame({"Age": [20, 30]})
    app.session_state["result"] = AgentResponse(
        type="text",
        answer="## نتیجه\n\nمیانگین Age برابر 25 است.\n\n## Summary\n\nMean Age is 25.",
    )
    app.run(timeout=20)

    rendered = next(item.value for item in app.markdown if item.value.startswith('<section class="analysis-output">'))
    assert '<h2 dir="auto">نتیجه</h2>' in rendered
    assert '<h2 dir="auto">Summary</h2>' in rendered
