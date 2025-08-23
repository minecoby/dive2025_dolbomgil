from pydantic import BaseModel
from typing import Optional


class HomeInfoResponse(BaseModel):
    protector_name: str
    caree_name: str
    safe_zone_active: bool
    caree_in_safe_zone: Optional[bool]
    safe_zone_radius_meters: Optional[int]

    class Config:
        from_attributes = True