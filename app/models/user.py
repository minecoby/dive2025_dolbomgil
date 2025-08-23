from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from db.base import Base


class User(Base):
    __tablename__ = "User"
    
    user_id = Column(String(50), primary_key=True)
    name = Column(String(100), nullable=False)
    phone_number = Column(String(20), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    
    # 관계 설정
    carees = relationship("Caree", back_populates="creator")
    relationships = relationship("UserRelationship", back_populates="protector")
    position_histories = relationship("PositionHistory", back_populates="user")
    fcm_tokens = relationship("FCMToken", back_populates="user")