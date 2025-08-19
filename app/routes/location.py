from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from db.session import get_db
from crud.location import (
    update_protector_location, 
    update_caree_location,
    get_latest_protector_location,
    get_latest_caree_location
)
from crud.caree import get_carees_by_user
from schema.location import LocationUpdateRequest, LocationUpdateResponse, LocationResponse, BothLocationResponse
from utils.auth import get_current_user_id
from utils.watch_auth import get_caree_from_registration_code
from models.caree import Caree

router = APIRouter(prefix="/api/location", tags=["location"])


@router.post("/protector", response_model=LocationUpdateResponse)
async def update_protector_location_endpoint(
    location_data: LocationUpdateRequest,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """보호자 위치 업데이트"""
    try:
        updated_location = update_protector_location(db, current_user_id, location_data)
        
        return LocationUpdateResponse(
            success=True,
            message="보호자 위치가 업데이트되었습니다.",
            location=LocationResponse.from_orm(updated_location)
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"보호자 위치 업데이트 실패: {str(e)}"
        )


@router.post("/caree", response_model=LocationUpdateResponse)
async def update_caree_location_endpoint(
    location_data: LocationUpdateRequest,
    caree: Caree = Depends(get_caree_from_registration_code),
    db: Session = Depends(get_db)
):
    """피보호자 위치 업데이트"""
    try:
        updated_location = update_caree_location(db, caree.caree_id, location_data)
        
        return LocationUpdateResponse(
            success=True,
            message="피보호자 위치가 업데이트되었습니다.",
            location=LocationResponse.from_orm(updated_location)
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"피보호자 위치 업데이트 실패: {str(e)}"
        )


@router.get("/both", response_model=BothLocationResponse)
async def get_both_locations(
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """보호자와 피보호자의 최신 위치 조회"""
    try:
        # 보호자 위치
        protector_location = get_latest_protector_location(db, current_user_id)
        
        # 피보호자 위치
        carees = get_carees_by_user(db, current_user_id)
        caree_location = None
        if carees:
            caree_location = get_latest_caree_location(db, carees[0].caree_id)
        
        return BothLocationResponse(
            protector_location=LocationResponse.from_orm(protector_location) if protector_location else None,
            caree_location=LocationResponse.from_orm(caree_location) if caree_location else None
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"위치 조회 실패: {str(e)}"
        )