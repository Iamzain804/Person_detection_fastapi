from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_read_root():
    """Test standard root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    # Check core fields
    assert data["message"] == "Welcome to Person Detection API"
    assert data["status"] == "running"
    # Check if server_time exists (dynamic value, so we just check presence)
    assert "server_time" in data

def test_detect_no_auth():
    """Test that detection fails without API key"""
    response = client.post("/api/v1/detect")
    assert response.status_code == 401 # Unauthorized
