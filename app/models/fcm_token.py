from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db.base import Base


class FCMToken(Base):
    __tablename__ = "fcm_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(50), ForeignKey("User.user_id"), nullable=False)
    fcm_token = Column(String(500), nullable=False, unique=True)
    device_type = Column(String(20), nullable=True)  # android, ios, web
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # 관계 설정
    user = relationship("User", back_populates="fcm_tokens")
