from pydantic import BaseModel, Field
from typing import Optional


class SafeZoneLocationRequest(BaseModel):
    center_latitude: float = Field(..., ge=-90, le=90)
    center_longitude: float = Field(..., ge=-180, le=180)


class SafeZoneRadiusRequest(BaseModel):
    radius_meters: int = Field(..., ge=10, le=5000)


class SafeZoneResponse(BaseModel):
    safe_zone_id: int
    caree_id: int
    zone_name: str
    center_latitude: float
    center_longitude: float
    radius_meters: int
    is_active: bool

    class Config:
        from_attributes = True


class SafeZoneUpdateResponse(BaseModel):
    success: bool
    message: str
    safe_zone: Optional[SafeZoneResponse] = None


class SafeZoneDeleteResponse(BaseModel):
    success: bool
    message: str