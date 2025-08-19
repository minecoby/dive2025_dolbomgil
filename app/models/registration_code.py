from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Index
from sqlalchemy.orm import relationship
from db.base import Base


class RegistrationCode(Base):
    __tablename__ = "RegistrationCode"
    
    code_id = Column(Integer, primary_key=True, autoincrement=True)
    caree_id = Column(Integer, ForeignKey("Caree.caree_id"), nullable=False)
    registration_code = Column(String(8), unique=True, nullable=False)
    is_used = Column(Boolean, default=False)
    
    # 관계 설정
    caree = relationship("Caree", back_populates="registration_codes")
    
    # 인덱스 설정
    __table_args__ = (
        Index('idx_registration_code', 'registration_code'),
    )