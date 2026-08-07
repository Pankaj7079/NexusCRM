"""Tests for Authentication API endpoints & JWT validation."""

import pytest


@pytest.mark.asyncio
async def test_register_and_login(client):
    """Test user registration and subsequent login."""
    reg_payload = {
        "email": "newuser@nexuscrm.io",
        "password": "securepassword",
        "full_name": "New Developer",
        "role": "sales_rep",
    }
    reg_resp = await client.post("/api/v1/auth/register", json=reg_payload)
    assert reg_resp.status_code == 201
    data = reg_resp.json()
    assert data["email"] == "newuser@nexuscrm.io"
    assert "id" in data

    # Login
    login_resp = await client.post(
        "/api/v1/auth/login",
        data={"username": "newuser@nexuscrm.io", "password": "securepassword"},
    )
    assert login_resp.status_code == 200
    token_data = login_resp.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_invalid_login_credentials(client):
    """Test login rejection with invalid credentials."""
    resp = await client.post(
        "/api/v1/auth/login",
        data={"username": "nonexistent@nexuscrm.io", "password": "wrongpassword"},
    )
    assert resp.status_code == 400
    assert "Incorrect email or password" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_get_me_success_and_invalid_token(client, auth_headers):
    """Test fetching current profile with valid & invalid JWT auth headers."""
    # Valid Token
    resp = await client.get("/api/v1/auth/me", headers=auth_headers)
    assert resp.status_code == 200
    profile = resp.json()
    assert profile["email"] == "testuser@nexuscrm.io"

    # Invalid Token Header
    bad_headers = {"Authorization": "Bearer invalid.jwt.token"}
    bad_resp = await client.get("/api/v1/auth/me", headers=bad_headers)
    assert bad_resp.status_code == 401
    assert "Invalid authentication credentials" in bad_resp.json()["detail"]
