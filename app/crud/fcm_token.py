from sqlalchemy.orm import Session
from models.fcm_token import FCMToken
from typing import List, Optional


def create_fcm_token(
    db: Session, 
    user_id: str, 
    fcm_token: str, 
    device_type: str = None
) -> FCMToken:
    """FCM 토큰 생성 또는 업데이트"""
    # 기존 토큰이 있는지 확인
    existing_token = db.query(FCMToken).filter(
        FCMToken.fcm_token == fcm_token
    ).first()
    
    if existing_token:
        # 기존 토큰이 다른 사용자에게 할당되어 있다면 업데이트
        if existing_token.user_id != user_id:
            existing_token.user_id = user_id
            existing_token.device_type = device_type
            existing_token.is_active = True
            db.commit()
            db.refresh(existing_token)
            return existing_token
        else:
            # 같은 사용자의 토큰이면 활성화만
            existing_token.is_active = True
            existing_token.device_type = device_type
            db.commit()
            db.refresh(existing_token)
            return existing_token
    
    # 새 토큰 생성
    new_token = FCMToken(
        user_id=user_id,
        fcm_token=fcm_token,
        device_type=device_type,
        is_active=True
    )
    db.add(new_token)
    db.commit()
    db.refresh(new_token)
    return new_token


def get_user_fcm_tokens(db: Session, user_id: str) -> List[FCMToken]:
    """사용자의 모든 활성 FCM 토큰 조회"""
    return db.query(FCMToken).filter(
        FCMToken.user_id == user_id,
        FCMToken.is_active == True
    ).all()


def deactivate_fcm_token(db: Session, fcm_token: str) -> bool:
    """FCM 토큰 비활성화"""
    token = db.query(FCMToken).filter(FCMToken.fcm_token == fcm_token).first()
    if token:
        token.is_active = False
        db.commit()
        return True
    return False


def delete_fcm_token(db: Session, fcm_token: str) -> bool:
    """FCM 토큰 삭제"""
    token = db.query(FCMToken).filter(FCMToken.fcm_token == fcm_token).first()
    if token:
        db.delete(token)
        db.commit()
        return True
    return False


def update_device_type(
    db: Session, 
    fcm_token: str, 
    device_type: str
) -> Optional[FCMToken]:
    """디바이스 타입 업데이트"""
    token = db.query(FCMToken).filter(FCMToken.fcm_token == fcm_token).first()
    if token:
        token.device_type = device_type
        db.commit()
        db.refresh(token)
        return token
    return None
