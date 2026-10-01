from datetime import datetime, timedelta, timezone
import bcrypt
import jwt
from app.core.config import settings


def get_password_hash(password: str) -> str:
  """Hash a plain password with a random bcrypt salt."""
  salt = bcrypt.gensalt()
  return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
  """Verify plain password against stored bcrypt hash."""
  return bcrypt.checkpw(
      plain_password.encode("utf-8"), hashed_password.encode("utf-8")
  )


def create_access_token(
    data: dict, expires_delta: timedelta | None = None
) -> str:
  """Create a cryptographically signed JWT token."""
  to_encode = data.copy()
  if expires_delta:
    expire = datetime.now(timezone.utc) + expires_delta
  else:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
  to_encode.update({"exp": expire})
  return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> dict:
  """Decode and verify JWT signature & expiration."""
  return jwt.decode(
      token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
  )