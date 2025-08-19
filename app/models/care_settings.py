from sqlalchemy import Column, Integer, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from db.base import Base


class CareSettings(Base):
    __tablename__ = "CareSettings"
    
    setting_id = Column(Integer, primary_key=True, autoincrement=True)
    caree_id = Column(Integer, ForeignKey("Caree.caree_id"), nullable=False)
    care_mode_enabled = Column(Boolean, default=False)
    geofence_alerts_enabled = Column(Boolean, default=True)
    
    # 관계 설정
    caree = relationship("Caree", back_populates="care_settings")
    
    # 제약 조건
    __table_args__ = (
        UniqueConstraint('caree_id', name='unique_caree_settings'),
    )