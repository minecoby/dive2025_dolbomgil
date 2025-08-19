from pydantic import BaseModel, Field
from typing import Optional


class UserRegisterRequest(BaseModel):
    user_id: str = Field(..., min_length=3, max_length=50)
    name: str = Field(..., min_length=1, max_length=100)
    phone_number: str = Field(..., min_length=10, max_length=20)
    password: str = Field(..., min_length=6)
    device_token: Optional[str] = None


class UserResponse(BaseModel):
    user_id: str
    name: str
    phone_number: str
    device_token: Optional[str]

    class Config:
        from_attributes = True


class UserRegisterResponse(BaseModel):
    success: bool
    message: str
    user: Optional[UserResponse] = None