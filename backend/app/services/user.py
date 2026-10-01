import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash, verify_password
from app.models.user import User
from app.schemas.user import UserCreate


class UserService:

    @staticmethod
    async def get_by_email(db: AsyncSession, email: str) -> User | None:
        """Fetch a single user by unique email."""
        stmt = select(User).where(User.email == email)
        return await db.scalar(stmt)

    @staticmethod
    async def get_by_id(db: AsyncSession, user_id: uuid.UUID) -> User | None:
        """Fetch a single user by primary key UUID."""
        stmt = select(User).where(User.id == user_id)
        return await db.scalar(stmt)

    @staticmethod
    async def create_user(db: AsyncSession, *, user_in: UserCreate) -> User:
        """Register a new user after verifying unique email and hashing password."""
        existing_user = await UserService.get_by_email(db, email=user_in.email)
        if existing_user:
            raise ValueError("A user with this email already exists")

        # Hash plain password using bcrypt
        hashed_password = get_password_hash(user_in.password)

        db_user = User(
            email=user_in.email,
            hashed_password=hashed_password,
            is_active=True,
        )
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        return db_user

    @staticmethod
    async def authenticate(
        db: AsyncSession, *, email: str, password: str
    ) -> User | None:
        """Authenticate user by checking email, password hash, and active status."""
        user = await UserService.get_by_email(db, email=email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        if not user.is_active:
            return None
        return user