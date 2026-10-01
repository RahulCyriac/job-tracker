from httpx import ASGITransport, AsyncClient
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decode_access_token
from app.db.session import get_db
from app.main import app




@pytest.mark.asyncio
async def test_signup_endpoint_success(async_client: AsyncClient):
    payload = {
        "email": "sarah@example.com",
        "password": "strongpassword123",
    }
    res = await async_client.post("/api/v1/auth/signup", json=payload)
    assert res.status_code == 201

    data = res.json()
    assert data["email"] == "sarah@example.com"
    assert data["is_active"] is True
    assert "id" in data
    # Passwords and hashes must NEVER leak in responses
    assert "password" not in data
    assert "hashed_password" not in data


@pytest.mark.asyncio
async def test_signup_endpoint_duplicate_email(async_client: AsyncClient):
    payload = {
        "email": "duplicate@example.com",
        "password": "password123",
    }
    res1 = await async_client.post("/api/v1/auth/signup", json=payload)
    assert res1.status_code == 201

    res2 = await async_client.post("/api/v1/auth/signup", json=payload)
    assert res2.status_code == 400
    assert "already exists" in res2.json()["detail"]


@pytest.mark.asyncio
async def test_login_endpoint_success(async_client: AsyncClient):
    # 1. Sign up user
    signup_payload = {
        "email": "john@example.com",
        "password": "secretpassword",
    }
    signup_res = await async_client.post("/api/v1/auth/signup", json=signup_payload)
    assert signup_res.status_code == 201
    user_id = signup_res.json()["id"]

    # 2. Login
    login_payload = {
        "email": "john@example.com",
        "password": "secretpassword",
    }
    login_res = await async_client.post("/api/v1/auth/login", json=login_payload)
    assert login_res.status_code == 200

    token_data = login_res.json()
    assert token_data["token_type"] == "bearer"
    assert "access_token" in token_data

    # 3. Verify decoded token subject matches user ID
    payload = decode_access_token(token_data["access_token"])
    assert payload["sub"] == user_id


@pytest.mark.asyncio
async def test_login_endpoint_invalid_password(async_client: AsyncClient):
    # 1. Sign up user
    await async_client.post(
        "/api/v1/auth/signup",
        json={"email": "wrongpw@example.com", "password": "correctpassword"},
    )

    # 2. Login with wrong password
    login_res = await async_client.post(
        "/api/v1/auth/login",
        json={"email": "wrongpw@example.com", "password": "incorrectpassword"},
    )
    assert login_res.status_code == 401
    assert login_res.json()["detail"] == "Incorrect email or password"


@pytest.mark.asyncio
async def test_login_endpoint_nonexistent_user(async_client: AsyncClient):
    login_res = await async_client.post(
        "/api/v1/auth/login",
        json={"email": "ghost@example.com", "password": "somepassword"},
    )
    assert login_res.status_code == 401
    assert login_res.json()["detail"] == "Incorrect email or password"
