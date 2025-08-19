from sqlalchemy import Column, Integer, ForeignKey, Enum, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship
from db.base import Base
import enum


class RelationshipType(enum.Enum):
    primary = "primary"
    secondary = "secondary"
    emergency_contact = "emergency_contact"


class UserRelationship(Base):
    __tablename__ = "UserRelationship"
    
    relationship_id = Column(Integer, primary_key=True, autoincrement=True)
    protector_user_id = Column(String(50), ForeignKey("User.user_id"), nullable=False)
    caree_id = Column(Integer, ForeignKey("Caree.caree_id"), nullable=False)
    relationship_type = Column(Enum(RelationshipType), default=RelationshipType.primary)
    can_receive_alerts = Column(Boolean, default=True)
    can_modify_settings = Column(Boolean, default=True)
    
    # 관계 설정
    protector = relationship("User", back_populates="relationships")
    caree = relationship("Caree", back_populates="relationships")
    
    # 제약 조건
    __table_args__ = (
        UniqueConstraint('protector_user_id', 'caree_id', name='unique_relationship'),
    )