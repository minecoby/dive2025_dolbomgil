from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from db.session import get_db
from crud.safe_zone import (
    create_safe_zone,
    get_safe_zone_by_user,
    update_safe_zone,
    delete_safe_zone,
    toggle_safe_zone_active
)
from schema.safe_zone import (
    SafeZoneCreateRequest,
    SafeZoneUpdateRequest,
    SafeZoneResponse,
    SafeZoneCreateResponse,
    SafeZoneUpdateResponse,
    SafeZoneDeleteResponse
)
from utils.auth import get_current_user_id

router = APIRouter(prefix="/api/safezone", tags=["safezone"])


@router.post("/create", response_model=SafeZoneCreateResponse)
async def create_safe_zone_endpoint(
    safe_zone_data: SafeZoneCreateRequest,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """안전구역 생성/업데이트"""
    try:
        safe_zone = create_safe_zone(db, current_user_id, safe_zone_data)
        
        if not safe_zone:
            return SafeZoneCreateResponse(
                success=False,
                message="등록된 피보호자가 없습니다."
            )
        
        return SafeZoneCreateResponse(
            success=True,
            message="안전구역이 설정되었습니다.",
            safe_zone=SafeZoneResponse.from_orm(safe_zone)
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"안전구역 설정 실패: {str(e)}"
        )


@router.get("/info", response_model=SafeZoneResponse)
async def get_safe_zone_info(
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """현재 설정된 안전구역 정보 조회"""
    try:
        safe_zone = get_safe_zone_by_user(db, current_user_id)
        
        if not safe_zone:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="설정된 안전구역이 없습니다."
            )
        
        return SafeZoneResponse.from_orm(safe_zone)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"안전구역 조회 실패: {str(e)}"
        )


@router.put("/update", response_model=SafeZoneUpdateResponse)
async def update_safe_zone_endpoint(
    safe_zone_data: SafeZoneUpdateRequest,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """안전구역 부분 업데이트"""
    try:
        safe_zone = update_safe_zone(db, current_user_id, safe_zone_data)
        
        if not safe_zone:
            return SafeZoneUpdateResponse(
                success=False,
                message="설정된 안전구역이 없습니다."
            )
        
        return SafeZoneUpdateResponse(
            success=True,
            message="안전구역이 업데이트되었습니다.",
            safe_zone=SafeZoneResponse.from_orm(safe_zone)
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"안전구역 업데이트 실패: {str(e)}"
        )


@router.post("/toggle", response_model=SafeZoneUpdateResponse)
async def toggle_safe_zone_endpoint(
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """안전구역 활성화/비활성화 토글"""
    try:
        safe_zone = toggle_safe_zone_active(db, current_user_id)
        
        if not safe_zone:
            return SafeZoneUpdateResponse(
                success=False,
                message="설정된 안전구역이 없습니다."
            )
        
        status_text = "활성화" if safe_zone.is_active else "비활성화"
        return SafeZoneUpdateResponse(
            success=True,
            message=f"안전구역이 {status_text}되었습니다.",
            safe_zone=SafeZoneResponse.from_orm(safe_zone)
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"안전구역 토글 실패: {str(e)}"
        )


@router.delete("/delete", response_model=SafeZoneDeleteResponse)
async def delete_safe_zone_endpoint(
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """안전구역 삭제"""
    try:
        success = delete_safe_zone(db, current_user_id)
        
        if success:
            return SafeZoneDeleteResponse(
                success=True,
                message="안전구역이 삭제되었습니다."
            )
        else:
            return SafeZoneDeleteResponse(
                success=False,
                message="삭제할 안전구역이 없습니다."
            )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"안전구역 삭제 실패: {str(e)}"
        )