import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.user import UserCreate
from app.services.user import UserService


@pytest.mark.asyncio
async def test_create_user_success(db_session: AsyncSession):
    user_in = UserCreate(email="alice@example.com", password="securepassword123")
    user = await UserService.create_user(db_session, user_in=user_in)

    assert user.id is not None
    assert user.email == "alice@example.com"
    assert user.is_active is True
    # Password must never be stored as plaintext!
    assert user.hashed_password != "securepassword123"
    assert user.hashed_password.startswith("$2b$")


@pytest.mark.asyncio
async def test_create_user_duplicate_email_raises_error(db_session: AsyncSession):
    user_in1 = UserCreate(email="duplicate@example.com", password="password123")
    await UserService.create_user(db_session, user_in=user_in1)

    # Attempting to register the same email must raise ValueError
    user_in2 = UserCreate(email="duplicate@example.com", password="anotherpassword456")
    with pytest.raises(ValueError, match="already exists"):
        await UserService.create_user(db_session, user_in=user_in2)


@pytest.mark.asyncio
async def test_authenticate_user_success(db_session: AsyncSession):
    raw_pwd = "mysecretpassword"
    user_in = UserCreate(email="bob@example.com", password=raw_pwd)
    created_user = await UserService.create_user(db_session, user_in=user_in)

    authenticated_user = await UserService.authenticate(
        db_session, email="bob@example.com", password=raw_pwd
    )

    assert authenticated_user is not None
    assert authenticated_user.id == created_user.id
    assert authenticated_user.email == "bob@example.com"


@pytest.mark.asyncio
async def test_authenticate_user_invalid_credentials(db_session: AsyncSession):
    user_in = UserCreate(email="charlie@example.com", password="correctpassword")
    await UserService.create_user(db_session, user_in=user_in)

    # 1. Wrong password
    res_wrong_pw = await UserService.authenticate(
        db_session, email="charlie@example.com", password="wrongpassword"
    )
    assert res_wrong_pw is None

    # 2. Non-existent email
    res_unknown_email = await UserService.authenticate(
        db_session, email="nobody@example.com", password="correctpassword"
    )
    assert res_unknown_email is None