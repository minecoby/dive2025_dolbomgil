from sqlalchemy.orm import Session
from models.alert_history import AlertHistory, AlertType
from models.caree import Caree
from models.user import User
from datetime import datetime, timedelta
from typing import Optional


def create_alert(
    db: Session, 
    caree_id: int, 
    alert_type: AlertType, 
    message: str
) -> AlertHistory:
    """알림 기록 생성"""
    alert = AlertHistory(
        caree_id=caree_id,
        alert_type=alert_type,
        message=message
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert


def has_recent_alert(
    db: Session, 
    caree_id: int, 
    alert_type: AlertType, 
    minutes: int = 5
) -> bool:
    """최근 N분 내에 동일한 타입의 알림이 있는지 확인"""
    cutoff_time = datetime.now() - timedelta(minutes=minutes)
    
    recent_alert = db.query(AlertHistory).filter(
        AlertHistory.caree_id == caree_id,
        AlertHistory.alert_type == alert_type,
        AlertHistory.is_acknowledged == False,
        AlertHistory.created_at >= cutoff_time
    ).first()
    
    return recent_alert is not None




def create_geofence_breach_alert(db: Session, caree_id: int) -> Optional[AlertHistory]:
    """이탈 알림 생성"""
    
    # 중복 알림 방지: 최근 5분 내에 동일한 알림이 있으면 스킵
    if has_recent_alert(db, caree_id, AlertType.geofence_breach, 5):
        return None
    
    # 피보호자 정보 조회
    caree = db.query(Caree).filter(Caree.caree_id == caree_id).first()
    if not caree:
        return None
    
    message = f"{caree.name}님이 안전구역을 벗어났습니다."
    
    return create_alert(db, caree_id, AlertType.geofence_breach, message)


def create_low_battery_alert(db: Session, caree_id: int, battery_level: int) -> Optional[AlertHistory]:
    """배터리 부족 알림 생성"""
    
    # 중복 알림 방지: 최근 30분 내에 배터리 알림이 있으면 스킵
    if has_recent_alert(db, caree_id, AlertType.low_battery, 30):
        return None
    
    caree = db.query(Caree).filter(Caree.caree_id == caree_id).first()
    if not caree:
        return None
    
    message = f"{caree.name}님의 워치 배터리가 {battery_level}%입니다."
    
    return create_alert(db, caree_id, AlertType.low_battery, message)