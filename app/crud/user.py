from sqlalchemy.orm import Session
from models.user import User, UserRole
from models.registration_code import RegistrationCode
from passlib.context import CryptContext
import secrets
import string

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def generate_registration_code() -> str:
    return ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))


def create_protector(db: Session, name: str, phone_number: str, password: str, device_token: str = None) -> User:
    hashed_password = get_password_hash(password)
    user = User(
        name=name,
        phone_number=phone_number,
        password_hash=hashed_password,
        role=UserRole.protector,
        device_token=device_token
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def create_caree_with_code(db: Session, device_token: str = None) -> tuple[User, str]:
    user = User(
        role=UserRole.caree,
        device_token=device_token,
        password_hash=""  # H (¤ÌÜ tÜ
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # ñ] TÜ Ý1
    code_value = generate_registration_code()
    registration_code = RegistrationCode(
        caree_user_id=user.user_id,
        code_value=code_value
    )
    db.add(registration_code)
    db.commit()
    
    return user, code_value


def get_user_by_phone(db: Session, phone_number: str) -> User:
    return db.query(User).filter(User.phone_number == phone_number).first()


def get_user_by_code(db: Session, code_value: str) -> User:
    registration_code = db.query(RegistrationCode).filter(RegistrationCode.code_value == code_value).first()
    if registration_code:
        return db.query(User).filter(User.user_id == registration_code.caree_user_id).first()
    return None