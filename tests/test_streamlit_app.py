from streamlit.testing.v1 import AppTest
from pathlib import Path


def test_streamlit_demo_starts():
    app = AppTest.from_file("streamlit_app.py").run(timeout=20)
    assert not app.exception
    assert app.title[0].value.startswith("📊")
    assert "unicode-bidi: plaintext" in app.markdown[0].value


def test_streamlit_demo_accepts_the_persian_sample():
    path = next(Path("uploads").glob("1b39*.csv"))
    app = AppTest.from_file("streamlit_app.py").run(timeout=20)
    app.file_uploader[0].upload(path.name, path.read_bytes(), "text/csv").run(timeout=20)

    assert not app.exception
    assert [metric.value for metric in app.metric] == ["31", "10", "186"]
    assert app.text_area
