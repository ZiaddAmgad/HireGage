"""
Test cases for the HireGage API endpoints
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

# Create test client
client = TestClient(app)

def test_root():
    """Test the root API endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "Welcome to HireGage AI HR Interview Agent API" in response.json()["message"]

def test_health_check():
    """Test the health check endpoint"""
    response = client.get("/api/v1/system/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    assert "timestamp" in response.json()

@pytest.mark.skip(reason="Requires OpenAI API key")
def test_start_interview():
    response = client.post(
        "/api/interview/start",
        json={"job_title": "Software Engineer", "company_name": "Tech Corp"}
    )
    assert response.status_code == 200
    assert "session_id" in response.json()
    assert "message" in response.json()

# Add more tests for other endpoints
