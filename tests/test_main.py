from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_read_root():
    """Test standard root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to Person Detection API", "status": "running"}

def test_detect_no_auth():
    """Test that detection fails without API key"""
    response = client.post("/api/v1/detect")
    assert response.status_code == 401 # Unauthorized
