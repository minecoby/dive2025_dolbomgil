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
from crud.alert import create_geofence_breach_alert, create_low_battery_alert
from services.fcm_service import FCMService
from schema.location import LocationUpdateRequest, LocationUpdateResponse, LocationResponse, BothLocationResponse
from utils.auth import get_current_user_id
from utils.watch_auth import get_caree_from_registration_code
from models.caree import Caree
from models.safe_zone import SafeZone

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
    """피보호자 위치 업데이트 및 알림 처리"""
    try:
        updated_location, geofence_breach = update_caree_location(db, caree.caree_id, location_data)
        
        # FCM 서비스 초기화 (파일이 없으면 스킵)
        try:
            fcm_service = FCMService()
            
            if geofence_breach:
                # 안전구역이 활성화되어 있는지 확인
                safe_zone = db.query(SafeZone).filter(
                    SafeZone.caree_id == caree.caree_id,
                    SafeZone.is_active == True
                ).first()
                
                if safe_zone:
                    # DB에 알림 기록 생성
                    create_geofence_breach_alert(db, caree.caree_id)
                    # FCM 푸시 알림 전송
                    fcm_service.send_geofence_breach_notification(db, caree.caree_id, caree.name)
                else:
                    # 안전구역이 비활성화된 경우 알림 기록만 생성 (푸시 알림은 전송하지 않음)
                    create_geofence_breach_alert(db, caree.caree_id)
                    print(f"피보호자 {caree.caree_id}의 안전구역이 비활성화되어 있어 푸시 알림을 전송하지 않습니다.")
            
            if location_data.battery_level and location_data.battery_level <= 20:
                # DB에 알림 기록 생성
                create_low_battery_alert(db, caree.caree_id, location_data.battery_level)
                # FCM 푸시 알림 전송
                fcm_service.send_low_battery_notification(db, caree.caree_id, caree.name, location_data.battery_level)
                
        except Exception as e:
            # FCM 서비스 초기화 실패 시 로그만 남기고 계속 진행
            print(f"FCM 서비스 초기화 실패 (알림 기능 비활성화): {str(e)}")
            # DB 알림은 정상적으로 생성
            if geofence_breach:
                create_geofence_breach_alert(db, caree.caree_id)
            if location_data.battery_level and location_data.battery_level <= 20:
                create_low_battery_alert(db, caree.caree_id, location_data.battery_level)
        return LocationUpdateResponse(
            success=True,
            message="피보호자 위치가 업데이트되었습니다.",
            location=LocationResponse.from_orm(updated_location),
            care_level=caree.care_level
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