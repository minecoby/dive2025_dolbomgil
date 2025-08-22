from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, Enum, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db.base import Base
import enum


class AlertType(enum.Enum):
    geofence_breach = "geofence_breach"
    emergency_button = "emergency_button"
    low_battery = "low_battery"
    device_offline = "device_offline"


class AlertHistory(Base):
    __tablename__ = "AlertHistory"
    
    alert_id = Column(Integer, primary_key=True, autoincrement=True)
    caree_id = Column(Integer, ForeignKey("Caree.caree_id"), nullable=False)
    alert_type = Column(Enum(AlertType), nullable=False)
    message = Column(Text, nullable=True)
    is_acknowledged = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 관계 설정
    caree = relationship("Caree", back_populates="alert_histories")