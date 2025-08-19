from sqlalchemy import Column, Integer, String, Enum, Date, ForeignKey
from sqlalchemy.orm import relationship
from db.base import Base
import enum


class Gender(enum.Enum):
    male = "male"
    female = "female"


class PairingStatus(enum.Enum):
    pending = "pending"
    paired = "paired"
    disconnected = "disconnected"


class Caree(Base):
    __tablename__ = "Caree"
    
    caree_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    gender = Column(Enum(Gender), nullable=False)
    birth_date = Column(Date, nullable=True)
    pairing_status = Column(Enum(PairingStatus), default=PairingStatus.pending)
    watch_device_id = Column(String(255), nullable=True)
    watch_device_token = Column(String(255), nullable=True)
    created_by_user_id = Column(Integer, ForeignKey("User.user_id"), nullable=False)
    
    # 관계 설정
    creator = relationship("User", back_populates="carees")
    registration_codes = relationship("RegistrationCode", back_populates="caree")
    relationships = relationship("UserRelationship", back_populates="caree")
    safe_zones = relationship("SafeZone", back_populates="caree")
    care_settings = relationship("CareSettings", back_populates="caree", uselist=False)
    position_histories = relationship("PositionHistory", back_populates="caree")
    alert_histories = relationship("AlertHistory", back_populates="caree")