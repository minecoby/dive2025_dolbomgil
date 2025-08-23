from sqlalchemy.orm import Session
from models.safe_zone import SafeZone
from models.caree import Caree
from schema.safe_zone import SafeZoneLocationRequest, SafeZoneRadiusRequest
from typing import Optional


def get_caree_by_user(db: Session, user_id: str) -> Optional[Caree]:
    """보호자의 피보호자 조회"""
    return db.query(Caree).filter(Caree.created_by_user_id == user_id).first()


def get_or_create_safe_zone(db: Session, user_id: str) -> Optional[SafeZone]:
    """안전구역 조회 또는 생성 (없는 경우 기본값으로 생성)"""
    caree = get_caree_by_user(db, user_id)
    if not caree:
        return None
    
    safe_zone = db.query(SafeZone).filter(SafeZone.caree_id == caree.caree_id).first()
    
    if not safe_zone:
        # 안전구역이 없는 경우 기본값으로 생성
        safe_zone = SafeZone(
            caree_id=caree.caree_id,
            zone_name="Home",
            center_latitude=37.5665,  # 서울시청 기본값
            center_longitude=126.9780,
            radius_meters=100,  # 기본 반경 100m
            is_active=True
        )
        db.add(safe_zone)
        db.commit()
        db.refresh(safe_zone)
    
    return safe_zone


def update_safe_zone_location(db: Session, user_id: str, location_data: SafeZoneLocationRequest) -> Optional[SafeZone]:
    """안전구역 위치 업데이트"""
    safe_zone = get_or_create_safe_zone(db, user_id)
    if not safe_zone:
        return None
    
    safe_zone.center_latitude = location_data.center_latitude
    safe_zone.center_longitude = location_data.center_longitude
    
    db.commit()
    db.refresh(safe_zone)
    return safe_zone


def update_safe_zone_radius(db: Session, user_id: str, radius_data: SafeZoneRadiusRequest) -> Optional[SafeZone]:
    """안전구역 반경 업데이트"""
    safe_zone = get_or_create_safe_zone(db, user_id)
    if not safe_zone:
        return None
    
    safe_zone.radius_meters = radius_data.radius_meters
    
    db.commit()
    db.refresh(safe_zone)
    return safe_zone


def get_safe_zone_by_user(db: Session, user_id: str) -> Optional[SafeZone]:
    """보호자의 안전구역 조회"""
    caree = get_caree_by_user(db, user_id)
    if not caree:
        return None
    
    return db.query(SafeZone).filter(SafeZone.caree_id == caree.caree_id).first()


def delete_safe_zone(db: Session, user_id: str) -> bool:
    """안전구역 삭제"""
    safe_zone = get_safe_zone_by_user(db, user_id)
    if not safe_zone:
        return False
    
    db.delete(safe_zone)
    db.commit()
    return True


def toggle_safe_zone_active(db: Session, user_id: str) -> Optional[SafeZone]:
    """안전구역 활성화/비활성화 토글"""
    safe_zone = get_safe_zone_by_user(db, user_id)
    if not safe_zone:
        return None
    
    safe_zone.is_active = not safe_zone.is_active
    db.commit()
    db.refresh(safe_zone)
    return safe_zone