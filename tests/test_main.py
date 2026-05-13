from fastapi.testclient import TestClient
from app.main import app
import pytest

# Using a context manager for the client to be safer with newer versions
def test_read_root():
    """Test standard root endpoint"""
    with TestClient(app) as client:
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Welcome to Person Detection API"
        assert "server_time" in data

def test_detect_no_auth():
    """Test that detection fails without API key"""
    with TestClient(app) as client:
        response = client.post("/api/v1/detect")
        assert response.status_code == 401 # Unauthorized
