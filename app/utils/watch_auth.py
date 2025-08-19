from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from db.session import get_db
from crud.registration_code import get_registration_code_by_code
from models.caree import Caree

security = HTTPBearer()


async def get_caree_from_registration_code(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> Caree:
    """등록코드로 피보호자 인증"""
    registration_code = credentials.credentials
    
    code_record = get_registration_code_by_code(db, registration_code)
    if not code_record:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 등록코드입니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    caree = db.query(Caree).filter(Caree.caree_id == code_record.caree_id).first()
    if not caree:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="피보호자를 찾을 수 없습니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return caree