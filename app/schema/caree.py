from pydantic import BaseModel, Field
from typing import Optional
from datetime import date
from models.caree import Gender, PairingStatus


class CareeCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    gender: Gender
    birth_date: Optional[date] = None


class CareeResponse(BaseModel):
    caree_id: int
    name: str
    gender: Gender
    birth_date: Optional[date]
    pairing_status: PairingStatus
    watch_device_id: Optional[str]
    watch_device_token: Optional[str]
    created_by_user_id: str

    class Config:
        from_attributes = True


class CareeCreateResponse(BaseModel):
    success: bool
    message: str
    caree: Optional[CareeResponse] = None
    registration_code: Optional[str] = None


class CareeDeleteResponse(BaseModel):
    success: bool
    message: str