from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_returns_ok():
    response = client.get("/health")
    assert response.status_code == 200

def test_missing_post_returns_404():
    """PROBE: Bad input -> clean 4xx, never a 500"""
    response = client.get("/matching/posts/99999/images")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()

def test_create_post_missing_field_returns_422():
    response = client.post("/posts/", json={"title": "Missing content field"})
    assert response.status_code == 422