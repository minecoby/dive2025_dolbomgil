from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from db.session import get_db
from crud.user import create_user, get_user_by_id, get_user_by_phone
from schema.user import UserRegisterRequest, UserRegisterResponse, UserResponse

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