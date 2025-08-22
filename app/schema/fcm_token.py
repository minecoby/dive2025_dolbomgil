from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class FCMTokenCreate(BaseModel):
    fcm_token: str
    device_type: Optional[str] = None


class FCMTokenUpdate(BaseModel):
    device_type: Optional[str] = None
    is_active: Optional[bool] = None


class FCMTokenResponse(BaseModel):
    id: int
    user_id: str
    fcm_token: str
    device_type: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class FCMTokenListResponse(BaseModel):
    tokens: list[FCMTokenResponse]
    total_count: int
