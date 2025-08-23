from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from db.session import get_db
from crud.caree import get_carees_by_user
from models.user import User
from models.safe_zone import SafeZone
from models.position_history import PositionHistory, PositionType
from schema.home import HomeInfoResponse
from utils.auth import get_current_user_id

router = APIRouter(prefix="/api/home", tags=["home"])


@router.get("/info", response_model=HomeInfoResponse)
async def get_home_info(
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    try:
        # 보호자 정보 조회
        protector = db.query(User).filter(User.user_id == current_user_id).first()
        if not protector:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="사용자 정보를 찾을 수 없습니다."
            )

        # 피보호자 정보 조회
        carees = get_carees_by_user(db, current_user_id)
        if not carees:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="등록된 피보호자가 없습니다."
            )
        
        caree = carees[0]
        
        # SafeZone 정보 조회 (활성화된 것 우선)
        safe_zone = db.query(SafeZone).filter(
            SafeZone.caree_id == caree.caree_id,
            SafeZone.is_active == True
        ).first()
        
        if not safe_zone:
            # 활성화된 SafeZone이 없으면 가장 최근 것 조회
            safe_zone = db.query(SafeZone).filter(
                SafeZone.caree_id == caree.caree_id
            ).order_by(desc(SafeZone.safe_zone_id)).first()
        
        # 피보호자의 최신 위치 정보 조회
        latest_position = db.query(PositionHistory).filter(
            PositionHistory.caree_id == caree.caree_id,
            PositionHistory.position_type == PositionType.caree
        ).order_by(desc(PositionHistory.recorded_at)).first()
        
        # 응답 데이터 구성
        return HomeInfoResponse(
            protector_name=protector.name,
            caree_name=caree.name,
            safe_zone_active=safe_zone.is_active if safe_zone else False,
            caree_in_safe_zone=latest_position.is_inside_safe_zone if latest_position else None,
            safe_zone_radius_meters=safe_zone.radius_meters if safe_zone else None
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"홈 정보 조회 실패: {str(e)}"
        )