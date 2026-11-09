
from pydantic import BaseModel, EmailStr, Field, ConfigDict


# User registration request
class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


# User login request
class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


# Safe user response (never expose password_hash)
class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    email: EmailStr


# JWT token response
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
