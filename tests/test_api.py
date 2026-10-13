from fastapi.testclient import TestClient

from api import app

client = TestClient(app)


def test_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["ok"] is True


def test_video_id_validation():
    response = client.get("/api/videos/../../main.py")
    assert response.status_code in (400, 404)


def test_empty_text_is_rejected():
    response = client.post("/api/generate", json={"topic": "   "})
    assert response.status_code == 422
