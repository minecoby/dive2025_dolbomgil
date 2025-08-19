from sqlalchemy.orm import Session
from models.user import User
from passlib.context import CryptContext
from schema.user import UserRegisterRequest

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_user_by_id(db: Session, user_id: str) -> User:
    return db.query(User).filter(User.user_id == user_id).first()


def get_user_by_phone(db: Session, phone_number: str) -> User:
    return db.query(User).filter(User.phone_number == phone_number).first()


def create_user(db: Session, user_data: UserRegisterRequest) -> User:
    hashed_password = get_password_hash(user_data.password)
    user = User(
        user_id=user_data.user_id,
        name=user_data.name,
        phone_number=user_data.phone_number,
        password_hash=hashed_password,
        device_token=user_data.device_token
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user