from sqlalchemy.orm import Session
from models.registration_code import RegistrationCode
import secrets
import string


def generate_registration_code() -> str:
    return ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))


def create_registration_code(db: Session, caree_id: int) -> str:
    existing_code = db.query(RegistrationCode).filter(RegistrationCode.caree_id == caree_id).first()
    if existing_code:
        db.delete(existing_code)
    registration_code = generate_registration_code()

    while db.query(RegistrationCode).filter(RegistrationCode.registration_code == registration_code).first():
        registration_code = generate_registration_code()
    
    code_record = RegistrationCode(
        caree_id=caree_id,
        registration_code=registration_code
    )
    db.add(code_record)
    db.commit()
    
    return registration_code


def get_registration_code_by_code(db: Session, code: str) -> RegistrationCode:
    return db.query(RegistrationCode).filter(RegistrationCode.registration_code == code).first()


def get_registration_code_by_caree_id(db: Session, caree_id: int) -> RegistrationCode:
    return db.query(RegistrationCode).filter(RegistrationCode.caree_id == caree_id).first()


def mark_code_as_used(db: Session, code: str) -> bool:
    code_record = get_registration_code_by_code(db, code)
    if code_record and not code_record.is_used:
        code_record.is_used = True
        db.commit()
        return True
    return False