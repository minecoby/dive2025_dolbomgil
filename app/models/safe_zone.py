from sqlalchemy import Column, Integer, String, DECIMAL, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from db.base import Base


class SafeZone(Base):
    __tablename__ = "SafeZone"
    
    safe_zone_id = Column(Integer, primary_key=True, autoincrement=True)
    caree_id = Column(Integer, ForeignKey("Caree.caree_id"), nullable=False)
    zone_name = Column(String(100), default="Home")
    center_latitude = Column(DECIMAL(10, 7), nullable=False)
    center_longitude = Column(DECIMAL(10, 7), nullable=False)
    radius_meters = Column(Integer, nullable=False, default=100)
    is_active = Column(Boolean, default=True)
    
    # 관계 설정
    caree = relationship("Caree", back_populates="safe_zones")