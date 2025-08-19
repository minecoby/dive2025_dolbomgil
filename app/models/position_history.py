from sqlalchemy import Column, Integer, DECIMAL, DateTime, Float, Boolean, ForeignKey, String, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db.base import Base
import enum


class PositionType(enum.Enum):
    user = "user"
    caree = "caree"


class PositionHistory(Base):
    __tablename__ = "PositionHistory"
    
    position_id = Column(Integer, primary_key=True, autoincrement=True)
    position_type = Column(Enum(PositionType), nullable=False)
    user_id = Column(String(50), ForeignKey("User.user_id"), nullable=True)
    caree_id = Column(Integer, ForeignKey("Caree.caree_id"), nullable=True)
    latitude = Column(DECIMAL(10, 7), nullable=False)
    longitude = Column(DECIMAL(10, 7), nullable=False)
    accuracy_meters = Column(Float, nullable=True)
    battery_level = Column(Integer, nullable=True)
    is_inside_safe_zone = Column(Boolean, nullable=True)
    recorded_at = Column(DateTime, default=func.now())
    
    # 관계 설정
    user = relationship("User", back_populates="position_histories")
    caree = relationship("Caree", back_populates="position_histories")