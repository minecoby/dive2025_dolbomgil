from pydantic import BaseModel, Field
from typing import Optional


class SafeZoneCreateRequest(BaseModel):
    zone_name: str = Field(..., min_length=1, max_length=100)
    center_latitude: float = Field(..., ge=-90, le=90)
    center_longitude: float = Field(..., ge=-180, le=180)
    radius_meters: int = Field(..., ge=10, le=5000)


class SafeZoneUpdateRequest(BaseModel):
    zone_name: Optional[str] = Field(None, min_length=1, max_length=100)
    center_latitude: Optional[float] = Field(None, ge=-90, le=90)
    center_longitude: Optional[float] = Field(None, ge=-180, le=180)
    radius_meters: Optional[int] = Field(None, ge=10, le=5000)
    is_active: Optional[bool] = None


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


class SafeZoneCreateResponse(BaseModel):
    success: bool
    message: str
    safe_zone: Optional[SafeZoneResponse] = None


class SafeZoneUpdateResponse(BaseModel):
    success: bool
    message: str
    safe_zone: Optional[SafeZoneResponse] = None


class SafeZoneDeleteResponse(BaseModel):
    success: bool
    message: str