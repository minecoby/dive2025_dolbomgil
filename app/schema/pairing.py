from pydantic import BaseModel, Field
from typing import Optional


class WatchPairingRequest(BaseModel):
    registration_code: str = Field(..., min_length=6, max_length=8)
    watch_device_id: Optional[str] = Field(None, max_length=255)
    watch_device_token: Optional[str] = Field(None, max_length=255)


class WatchPairingResponse(BaseModel):
    success: bool
    message: str
    caree_name: Optional[str] = None
    caree_id: Optional[int] = None