from sqlalchemy.orm import Session
from models.caree import Caree, PairingStatus
from models.registration_code import RegistrationCode
from crud.registration_code import get_registration_code_by_code, mark_code_as_used
from schema.pairing import WatchPairingRequest
from typing import Optional


def pair_watch_with_caree(db: Session, pairing_data: WatchPairingRequest) -> Optional[Caree]:
    """워치와 피보호자 페어링"""
    
    code_record = get_registration_code_by_code(db, pairing_data.registration_code)
    if not code_record:
        return None
    
    if code_record.is_used:
        return None

    caree = db.query(Caree).filter(Caree.caree_id == code_record.caree_id).first()
    if not caree:
        return None
    
    if caree.pairing_status == PairingStatus.paired:
        return None
    
    caree.watch_device_id = pairing_data.watch_device_id
    caree.watch_device_token = pairing_data.watch_device_token
    caree.pairing_status = PairingStatus.paired
    
    mark_code_as_used(db, pairing_data.registration_code)
    
    db.commit()
    db.refresh(caree)
    
    return caree


def get_pairing_info_by_code(db: Session, registration_code: str) -> Optional[dict]:
    """등록코드로 페어링 정보 조회"""
    
    code_record = get_registration_code_by_code(db, registration_code)
    if not code_record or code_record.is_used:
        return None
    
    caree = db.query(Caree).filter(Caree.caree_id == code_record.caree_id).first()
    if not caree:
        return None
    
    # 이미 페어링된 경우
    if caree.pairing_status == PairingStatus.paired:
        return None
    
    return {
        "caree_id": caree.caree_id,
        "caree_name": caree.name,
        "gender": caree.gender.value,
        "birth_date": caree.birth_date,
        "pairing_status": caree.pairing_status.value
    }


def unpair_watch(db: Session, caree_id: int) -> bool:
    """워치 페어링 해제"""
    
    caree = db.query(Caree).filter(Caree.caree_id == caree_id).first()
    if not caree:
        return False
    
    caree.watch_device_id = None
    caree.watch_device_token = None
    caree.pairing_status = PairingStatus.pending
    
    db.commit()
    return True