import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_get_all_items():
    """Test equivalent to Java's @Test method"""
    response = client.get("/api/items")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert data[0]["name"] == "FastAPI Service"

def test_get_single_item():
    response = client.get("/api/items/1")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == 1
    assert data["name"] == "FastAPI Service"

def test_item_not_found():
    response = client.get("/api/items/999")
    assert response.status_code == 404
