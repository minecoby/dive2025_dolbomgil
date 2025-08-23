from pydantic import BaseModel, Field
from typing import Optional


class UserRegisterRequest(BaseModel):
    user_id: str = Field(..., min_length=3, max_length=50)
    name: str = Field(..., min_length=1, max_length=100)
    phone_number: str = Field(..., min_length=10, max_length=20)
    password: str = Field(..., min_length=6)


class UserResponse(BaseModel):
    user_id: str
    name: str
    phone_number: str

    class Config:
        from_attributes = True


class UserRegisterResponse(BaseModel):
    success: bool
    message: str
    user: Optional[UserResponse] = None


class UserLoginRequest(BaseModel):
    user_id: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)
    fcm_token: Optional[str] = None
    device_type: Optional[str] = None


class UserLoginResponse(BaseModel):
    success: bool
    message: str
    access_token: Optional[str] = None
    token_type: str = "bearer"
    user: Optional[UserResponse] = None


class UserLogoutResponse(BaseModel):
    success: bool
    message: str