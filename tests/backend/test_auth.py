import pytest
from app.models.database import User

def test_register_success(test_client):
    response = test_client.post("/api/auth/register", json={
        "username": "testuser1",
        "password": "testpass123"
    })
    assert response.status_code == 200
    assert response.json()["message"] == "User registered successfully."

def test_register_duplicate(test_client):
    # Register once
    test_client.post("/api/auth/register", json={
        "username": "testuser2",
        "password": "testpass123"
    })
    # Register again with same username
    response = test_client.post("/api/auth/register", json={
        "username": "testuser2",
        "password": "testpass123"
    })
    assert response.status_code == 400
    assert response.json()["detail"] == "Username already exists"

def test_login_success(test_client):
    # Register user first
    test_client.post("/api/auth/register", json={
        "username": "testuser3",
        "password": "testpass123"
    })
    response = test_client.post("/api/auth/login", json={
        "username": "testuser3",
        "password": "testpass123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"

def test_login_invalid_password(test_client):
    # Register user first
    test_client.post("/api/auth/register", json={
        "username": "testuser4",
        "password": "testpass123"
    })
    response = test_client.post("/api/auth/login", json={
        "username": "testuser4",
        "password": "wrongpass"
    })
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid username or password"

def test_login_nonexistent_user(test_client):
    response = test_client.post("/api/auth/login", json={
        "username": "nonexistent",
        "password": "irrelevant"
    })
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid username or password"