from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


class UserRegisterRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Full Name")
    email: EmailStr = Field(..., description="Valid Email Address")
    password: str = Field(..., min_length=6, max_length=128, description="Password (at least 6 characters)")


class UserLoginRequest(BaseModel):
    email: EmailStr = Field(..., description="Email Address")
    password: str = Field(..., min_length=1, description="Password")


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
