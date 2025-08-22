import firebase_admin
from firebase_admin import credentials, messaging
from sqlalchemy.orm import Session
from models.fcm_token import FCMToken
from models.user import User
from models.caree import Caree
from typing import List, Optional
import logging
import os

logger = logging.getLogger(__name__)


class FCMService:
    _instance = None
    _initialized = False
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(FCMService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, service_account_path: str = None):
        if self._initialized:
            return
            
        if service_account_path is None:
            service_account_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH", "/app/serviceAccountKey.json")
        """FCM 서비스 초기화"""
        try:
            # Firebase Admin SDK가 이미 초기화되었는지 확인
            try:
                firebase_admin.get_app()
                logger.info("Firebase 앱이 이미 초기화되어 있습니다.")
            except ValueError:
                # 초기화되지 않은 경우에만 초기화
                cred = credentials.Certificate(service_account_path)
                firebase_admin.initialize_app(cred)
                logger.info("FCM 서비스가 성공적으로 초기화되었습니다.")
            
            self._initialized = True
        except Exception as e:
            logger.error(f"FCM 서비스 초기화 실패: {str(e)}")
            raise
    
    def send_notification(
        self, 
        fcm_tokens: List[str], 
        title: str, 
        body: str, 
        data: Optional[dict] = None
    ) -> bool:
        """FCM 푸시 알림 전송"""
        if not fcm_tokens:
            logger.warning("전송할 FCM 토큰이 없습니다.")
            return False
        
        try:
            # 각 토큰에 대해 개별 메시지 전송
            success_count = 0
            for token in fcm_tokens:
                try:
                    message = messaging.Message(
                        token=token,
                        notification=messaging.Notification(
                            title=title,
                            body=body
                        ),
                        data=data or {},
                        android=messaging.AndroidConfig(
                            priority="high",
                            notification=messaging.AndroidNotification(
                                priority="high",
                                sound="default"
                            )
                        ),
                        apns=messaging.APNSConfig(
                            payload=messaging.APNSPayload(
                                aps=messaging.Aps(
                                    sound="default",
                                    badge=1
                                )
                            )
                        )
                    )
                    
                    response = messaging.send(message)
                    if response:
                        success_count += 1
                        
                except Exception as e:
                    logger.error(f"토큰 {token}에 알림 전송 실패: {str(e)}")
                    continue
            
            logger.info(f"FCM 알림 전송 완료: 성공 {success_count}, 실패 {len(fcm_tokens) - success_count}")
            
            return success_count > 0
            
        except Exception as e:
            logger.error(f"FCM 알림 전송 실패: {str(e)}")
            return False
    
    def send_geofence_breach_notification(
        self, 
        db: Session, 
        caree_id: int, 
        caree_name: str
    ) -> bool:
        """안전구역 이탈 알림 전송"""
        try:
            # 피보호자와 연결된 보호자들의 FCM 토큰 조회
            caree = db.query(Caree).filter(Caree.caree_id == caree_id).first()
            if not caree:
                logger.error(f"피보호자를 찾을 수 없습니다: {caree_id}")
                return False
            
            # 보호자 정보 조회
            protector = db.query(User).filter(User.user_id == caree.created_by_user_id).first()
            if not protector:
                logger.error(f"보호자를 찾을 수 없습니다: {caree.created_by_user_id}")
                return False
            
            # 보호자의 활성 FCM 토큰들 조회
            fcm_tokens = db.query(FCMToken.fcm_token).filter(
                FCMToken.user_id == protector.user_id,
                FCMToken.is_active == True
            ).all()
            
            if not fcm_tokens:
                logger.warning(f"보호자 {protector.user_id}의 활성 FCM 토큰이 없습니다.")
                return False
            
            token_list = [token[0] for token in fcm_tokens]
            
            # 알림 전송
            title = "안전구역 이탈 알림"
            body = f"{caree_name}님이 안전구역을 벗어났습니다."
            data = {
                "type": "geofence_breach",
                "caree_id": str(caree_id),
                "caree_name": caree_name,
                "timestamp": str(caree.updated_at) if caree.updated_at else ""
            }
            
            return self.send_notification(token_list, title, body, data)
            
        except Exception as e:
            logger.error(f"안전구역 이탈 알림 전송 실패: {str(e)}")
            return False
    
    def send_low_battery_notification(
        self, 
        db: Session, 
        caree_id: int, 
        caree_name: str, 
        battery_level: int
    ) -> bool:
        """배터리 부족 알림 전송"""
        try:
            # 피보호자와 연결된 보호자들의 FCM 토큰 조회
            caree = db.query(Caree).filter(Caree.caree_id == caree_id).first()
            if not caree:
                logger.error(f"피보호자를 찾을 수 없습니다: {caree_id}")
                return False
            
            # 보호자 정보 조회
            protector = db.query(User).filter(User.user_id == caree.created_by_user_id).first()
            if not protector:
                logger.error(f"보호자를 찾을 수 없습니다: {caree.created_by_user_id}")
                return False
            
            # 보호자의 활성 FCM 토큰들 조회
            fcm_tokens = db.query(FCMToken.fcm_token).filter(
                FCMToken.user_id == protector.user_id,
                FCMToken.is_active == True
            ).all()
            
            if not fcm_tokens:
                logger.warning(f"보호자 {protector.user_id}의 활성 FCM 토큰이 없습니다.")
                return False
            
            token_list = [token[0] for token in fcm_tokens]
            
            # 알림 전송
            title = "배터리 부족 알림"
            body = f"{caree_name}님의 워치 배터리가 {battery_level}%입니다."
            data = {
                "type": "low_battery",
                "caree_id": str(caree_id),
                "caree_name": caree_name,
                "battery_level": str(battery_level),
                "timestamp": str(caree.updated_at) if hasattr(caree, 'updated_at') and caree.updated_at else ""
            }
            
            return self.send_notification(token_list, title, body, data)
            
        except Exception as e:
            logger.error(f"배터리 부족 알림 전송 실패: {str(e)}")
            return False
