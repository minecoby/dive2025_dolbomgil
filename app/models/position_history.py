from sqlalchemy import Column, Integer, DECIMAL, DateTime, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db.base import Base


class PositionHistory(Base):
    __tablename__ = "PositionHistory"
    
    position_id = Column(Integer, primary_key=True, autoincrement=True)
    caree_id = Column(Integer, ForeignKey("Caree.caree_id"), nullable=False)
    latitude = Column(DECIMAL(10, 7), nullable=False)
    longitude = Column(DECIMAL(10, 7), nullable=False)
    accuracy_meters = Column(Float, nullable=True)
    battery_level = Column(Integer, nullable=True)
    is_inside_safe_zone = Column(Boolean, nullable=True)
    recorded_at = Column(DateTime, default=func.now())
    
    # 관계 설정
    caree = relationship("Caree", back_populates="position_histories")