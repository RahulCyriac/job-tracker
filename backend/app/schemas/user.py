from datetime import datetime
import uuid
from pydantic import BaseModel, ConfigDict, EmailStr, Field


# Base schema containing shared attributes
class UserBase(BaseModel):
    email: EmailStr


# Payload for user registration
class UserCreate(UserBase):
    password: str = Field(min_length=8, description="Password must be at least 8 characters")


# Payload for user login
class UserLogin(BaseModel):
    email: EmailStr
    password: str


# Outgoing response returned to client (Notice: No passwords here!)
class UserResponse(UserBase):
    id: uuid.UUID
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Outgoing response for successful login
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"