from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class LocationUpdateRequest(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    accuracy_meters: Optional[float] = None
    battery_level: Optional[int] = Field(None, ge=0, le=100)


class LocationResponse(BaseModel):
    position_id: int
    latitude: float
    longitude: float
    accuracy_meters: Optional[float]
    battery_level: Optional[int]
    is_inside_safe_zone: Optional[bool]
    recorded_at: datetime

    class Config:
        from_attributes = True


class LocationUpdateResponse(BaseModel):
    success: bool
    message: str
    location: Optional[LocationResponse] = None
    care_level: Optional[int] = None


class BothLocationResponse(BaseModel):
    protector_location: Optional[LocationResponse] = None
    caree_location: Optional[LocationResponse] = None