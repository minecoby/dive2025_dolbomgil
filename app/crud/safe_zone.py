from sqlalchemy.orm import Session
from models.safe_zone import SafeZone
from models.caree import Caree
from schema.safe_zone import SafeZoneCreateRequest, SafeZoneUpdateRequest
from typing import Optional


def get_caree_by_user(db: Session, user_id: str) -> Optional[Caree]:
    """보호자의 피보호자 조회"""
    return db.query(Caree).filter(Caree.created_by_user_id == user_id).first()


def create_safe_zone(db: Session, user_id: str, safe_zone_data: SafeZoneCreateRequest) -> Optional[SafeZone]:
    """안전구역 생성 및 업데이트"""
    caree = get_caree_by_user(db, user_id)
    if not caree:
        return None
    
    existing_zone = db.query(SafeZone).filter(SafeZone.caree_id == caree.caree_id).first()
    
    if existing_zone:
        existing_zone.zone_name = safe_zone_data.zone_name
        existing_zone.center_latitude = safe_zone_data.center_latitude
        existing_zone.center_longitude = safe_zone_data.center_longitude
        existing_zone.radius_meters = safe_zone_data.radius_meters
        existing_zone.is_active = True
        db.commit()
        db.refresh(existing_zone)
        return existing_zone
    else:
        new_zone = SafeZone(
            caree_id=caree.caree_id,
            zone_name=safe_zone_data.zone_name,
            center_latitude=safe_zone_data.center_latitude,
            center_longitude=safe_zone_data.center_longitude,
            radius_meters=safe_zone_data.radius_meters,
            is_active=True
        )
        db.add(new_zone)
        db.commit()
        db.refresh(new_zone)
        return new_zone


def get_safe_zone_by_user(db: Session, user_id: str) -> Optional[SafeZone]:
    """보호자의 안전구역 조회"""
    caree = get_caree_by_user(db, user_id)
    if not caree:
        return None
    
    return db.query(SafeZone).filter(SafeZone.caree_id == caree.caree_id).first()


def update_safe_zone(db: Session, user_id: str, safe_zone_data: SafeZoneUpdateRequest) -> Optional[SafeZone]:
    """안전구역 업데이트"""
    safe_zone = get_safe_zone_by_user(db, user_id)
    if not safe_zone:
        return None
    
    if safe_zone_data.zone_name is not None:
        safe_zone.zone_name = safe_zone_data.zone_name
    if safe_zone_data.center_latitude is not None:
        safe_zone.center_latitude = safe_zone_data.center_latitude
    if safe_zone_data.center_longitude is not None:
        safe_zone.center_longitude = safe_zone_data.center_longitude
    if safe_zone_data.radius_meters is not None:
        safe_zone.radius_meters = safe_zone_data.radius_meters
    if safe_zone_data.is_active is not None:
        safe_zone.is_active = safe_zone_data.is_active
    
    db.commit()
    db.refresh(safe_zone)
    return safe_zone


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