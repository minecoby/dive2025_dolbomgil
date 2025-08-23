from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from db.session import get_db
from crud.user import create_user, get_user_by_id, get_user_by_phone, verify_password
from crud.fcm_token import update_user_fcm_token
from schema.user import UserRegisterRequest, UserRegisterResponse, UserResponse, UserLoginRequest, UserLoginResponse
from utils.jwt import create_access_token

router = APIRouter(prefix="/api/user", tags=["user"])


@router.post("/register", response_model=UserRegisterResponse)
async def register_user(user_data: UserRegisterRequest, db: Session = Depends(get_db)):
    existing_user = get_user_by_id(db, user_data.user_id)
    if existing_user:
        return UserRegisterResponse(
            success=False,
            message="이미 존재하는 아이디입니다."
        )
    
    existing_phone = get_user_by_phone(db, user_data.phone_number)
    if existing_phone:
        return UserRegisterResponse(
            success=False,
            message="이미 존재하는 전화번호입니다."
        )
    
    try:
        new_user = create_user(db, user_data)
        
        return UserRegisterResponse(
            success=True,
            message="성공적으로 회원가입되었습니다.",
            user=UserResponse.from_orm(new_user)
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )


@router.post("/login", response_model=UserLoginResponse)
async def login_user(login_data: UserLoginRequest, db: Session = Depends(get_db)):
    user = get_user_by_id(db, login_data.user_id)
    if not user:
        return UserLoginResponse(
            success=False,
            message="존재하지 않는 아이디입니다."
        )
    
    if not verify_password(login_data.password, user.password_hash):
        return UserLoginResponse(
            success=False,
            message="비밀번호가 틀렸습니다."
        )
    
    try:
        access_token = create_access_token(data={"sub": user.user_id})
        
        if login_data.fcm_token:
            update_user_fcm_token(
                db=db,
                user_id=user.user_id,
                new_fcm_token=login_data.fcm_token,
                device_type=login_data.device_type
            )
        
        return UserLoginResponse(
            success=True,
            message="로그인 성공",
            access_token=access_token,
            user=UserResponse.from_orm(user)
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {str(e)}"
        )