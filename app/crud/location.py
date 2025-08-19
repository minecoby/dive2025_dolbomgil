from sqlalchemy.orm import Session
from models.position_history import PositionHistory, PositionType
from models.safe_zone import SafeZone
from schema.location import LocationUpdateRequest
from typing import Optional
import math


def is_inside_safe_zone(latitude: float, longitude: float, caree_id: int, db: Session) -> bool:
    safe_zones = db.query(SafeZone).filter(
        SafeZone.caree_id == caree_id,
        SafeZone.is_active == True
    ).all()
    
    for zone in safe_zones:
        # 하버사인 공식
        distance = calculate_distance(
            latitude, longitude, 
            float(zone.center_latitude), float(zone.center_longitude)
        )
        if distance <= zone.radius_meters:
            return True
    
    return False


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371000  
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    a = (math.sin(delta_lat / 2) ** 2 +
         math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return R * c


def update_protector_location(db: Session, user_id: str, location_data: LocationUpdateRequest) -> PositionHistory:
    existing_position = db.query(PositionHistory).filter(
        PositionHistory.position_type == PositionType.user,
        PositionHistory.user_id == user_id
    ).first()
    
    if existing_position:
        existing_position.latitude = location_data.latitude
        existing_position.longitude = location_data.longitude
        existing_position.accuracy_meters = location_data.accuracy_meters
        existing_position.battery_level = location_data.battery_level
        existing_position.recorded_at = db.execute("SELECT NOW()").scalar()
        db.commit()
        db.refresh(existing_position)
        return existing_position
    else:
        new_position = PositionHistory(
            position_type=PositionType.user,
            user_id=user_id,
            latitude=location_data.latitude,
            longitude=location_data.longitude,
            accuracy_meters=location_data.accuracy_meters,
            battery_level=location_data.battery_level
        )
        db.add(new_position)
        db.commit()
        db.refresh(new_position)
        return new_position


def update_caree_location(db: Session, caree_id: int, location_data: LocationUpdateRequest) -> tuple[PositionHistory, bool]:
    """피보호자 위치 업데이트 및 이탈 감지"""
    current_inside_safe_zone = is_inside_safe_zone(location_data.latitude, location_data.longitude, caree_id, db)
    geofence_breach = False
    
    existing_position = db.query(PositionHistory).filter(
        PositionHistory.position_type == PositionType.caree,
        PositionHistory.caree_id == caree_id
    ).first()
    
    if existing_position:
        #이탈 감지: 안전구역 내부 -> 외부
        previous_inside_safe_zone = existing_position.is_inside_safe_zone
        if previous_inside_safe_zone == True and current_inside_safe_zone == False:
            geofence_breach = True
        
        # 위치 업데이트
        existing_position.latitude = location_data.latitude
        existing_position.longitude = location_data.longitude
        existing_position.accuracy_meters = location_data.accuracy_meters
        existing_position.battery_level = location_data.battery_level
        existing_position.is_inside_safe_zone = current_inside_safe_zone
        existing_position.recorded_at = db.execute("SELECT NOW()").scalar()
        db.commit()
        db.refresh(existing_position)
        return existing_position, geofence_breach
    else:
        new_position = PositionHistory(
            position_type=PositionType.caree,
            caree_id=caree_id,
            latitude=location_data.latitude,
            longitude=location_data.longitude,
            accuracy_meters=location_data.accuracy_meters,
            battery_level=location_data.battery_level,
            is_inside_safe_zone=current_inside_safe_zone
        )
        db.add(new_position)
        db.commit()
        db.refresh(new_position)
        return new_position, False


def get_latest_protector_location(db: Session, user_id: str) -> Optional[PositionHistory]:
    return db.query(PositionHistory).filter(
        PositionHistory.position_type == PositionType.user,
        PositionHistory.user_id == user_id
    ).first()


def get_latest_caree_location(db: Session, caree_id: int) -> Optional[PositionHistory]:
    return db.query(PositionHistory).filter(
        PositionHistory.position_type == PositionType.caree,
        PositionHistory.caree_id == caree_id
    ).first()