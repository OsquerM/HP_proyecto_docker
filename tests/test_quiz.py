from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_home():
    response = client.get("/")
    assert response.status_code == 200

def test_quiz_page():
    response = client.get("/quiz")
    assert response.status_code == 200