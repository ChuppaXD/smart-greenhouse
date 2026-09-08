from fastapi.testclient import TestClient

from main import app


client = TestClient(app)


def test_health():
    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()

    assert "status" in data
    assert "db" in data
    assert data["db"] in ("ok", "fail")