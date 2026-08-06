from fastapi.testclient import TestClient

from app.api import analyze
from app.main import app
from app.schemas.agent_schema import AgentResponse
from app.services import file_service


def test_file_profile_and_analysis_endpoints(tmp_path, monkeypatch):
    monkeypatch.setattr(file_service, "UPLOAD_DIR", tmp_path)
    client = TestClient(app)

    uploaded = client.post(
        "/upload",
        files={"file": ("data.csv", "Age,BMI\n20,21\n30,25", "text/csv")},
    )
    assert uploaded.status_code == 200
    file_id = uploaded.json()["file_id"]

    info = client.get(f"/files/{file_id}")
    profile = client.get(f"/profile/{file_id}")
    assert info.json()["column_names"] == ["Age", "BMI"]
    assert profile.json()["rows"] == 2

    monkeypatch.setattr(
        analyze,
        "run_agent",
        lambda *_: AgentResponse(type="text", answer="**Mean:** 25"),
    )
    response = client.post("/analyze/", json={"file_id": file_id, "question": "میانگین سن؟"})
    assert response.status_code == 200
    assert response.json()["answer"] == "**Mean:** 25"
