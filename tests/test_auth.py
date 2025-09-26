"""
Tests for API key authentication.
"""
import pytest
from fastapi.testclient import TestClient
from src.server import app

client = TestClient(app)

# Test cases for API key authentication
def test_health_check():
    """Test that the health check endpoint is publicly accessible."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_protected_endpoint_no_api_key():
    """Test that protected endpoints require an API key."""
    response = client.get("/")
    assert response.status_code == 403
    assert "Not authenticated" in response.text

def test_protected_endpoint_invalid_api_key():
    """Test that protected endpoints reject invalid API keys."""
    response = client.get(
        "/",
        headers={"X-API-Key": "invalid-key"}
    )
    assert response.status_code == 403
    assert "Invalid API Key" in response.text

@pytest.mark.parametrize("api_key", [
    "default-secure-key-123",
    "another-secure-key-456"
])
def test_protected_endpoint_valid_api_key(api_key):
    """Test that protected endpoints accept valid API keys."""
    response = client.get(
        "/",
        headers={"X-API-Key": api_key}
    )
    assert response.status_code == 200
    assert "message" in response.json()
    assert "version" in response.json()
    assert "environment" in response.json()
