from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from db.session import get_db
from crud.fcm_token import (
    create_fcm_token,
    get_user_fcm_tokens,
    deactivate_fcm_token,
    delete_fcm_token,
    update_device_type
)
from schema.fcm_token import (
    FCMTokenCreate,
    FCMTokenUpdate,
    FCMTokenResponse,
    FCMTokenListResponse
)
from utils.auth import get_current_user_id
from models.fcm_token import FCMToken

router = APIRouter(prefix="/api/fcm-token", tags=["fcm-token"])


@router.post("/", response_model=FCMTokenResponse)
async def register_fcm_token(
    token_data: FCMTokenCreate,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """FCM 토큰 등록"""
    try:
        fcm_token = create_fcm_token(
            db=db,
            user_id=current_user_id,
            fcm_token=token_data.fcm_token,
            device_type=token_data.device_type
        )
        
        return FCMTokenResponse.from_orm(fcm_token)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"FCM 토큰 등록 실패: {str(e)}"
        )


@router.get("/my-tokens", response_model=FCMTokenListResponse)
async def get_my_fcm_tokens(
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """내 FCM 토큰 목록 조회"""
    try:
        tokens = get_user_fcm_tokens(db, current_user_id)
        
        return FCMTokenListResponse(
            tokens=[FCMTokenResponse.from_orm(token) for token in tokens],
            total_count=len(tokens)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"FCM 토큰 조회 실패: {str(e)}"
        )


@router.put("/{fcm_token}", response_model=FCMTokenResponse)
async def update_fcm_token(
    fcm_token: str,
    token_update: FCMTokenUpdate,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """FCM 토큰 업데이트"""
    try:
        # 토큰 소유자 확인
        existing_token = db.query(FCMToken).filter(
            FCMToken.fcm_token == fcm_token,
            FCMToken.user_id == current_user_id
        ).first()
        
        if not existing_token:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="FCM 토큰을 찾을 수 없습니다."
            )
        
        if token_update.device_type is not None:
            updated_token = update_device_type(db, fcm_token, token_update.device_type)
            return FCMTokenResponse.from_orm(updated_token)
        
        return FCMTokenResponse.from_orm(existing_token)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"FCM 토큰 업데이트 실패: {str(e)}"
        )


@router.delete("/{fcm_token}")
async def remove_fcm_token(
    fcm_token: str,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """FCM 토큰 삭제"""
    try:
        # 토큰 소유자 확인
        existing_token = db.query(FCMToken).filter(
            FCMToken.fcm_token == fcm_token,
            FCMToken.user_id == current_user_id
        ).first()
        
        if not existing_token:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="FCM 토큰을 찾을 수 없습니다."
            )
        
        success = delete_fcm_token(db, fcm_token)
        
        if success:
            return {"message": "FCM 토큰이 성공적으로 삭제되었습니다."}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="FCM 토큰 삭제에 실패했습니다."
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"FCM 토큰 삭제 실패: {str(e)}"
        )


@router.post("/{fcm_token}/deactivate")
async def deactivate_token(
    fcm_token: str,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """FCM 토큰 비활성화"""
    try:
        # 토큰 소유자 확인
        existing_token = db.query(FCMToken).filter(
            FCMToken.fcm_token == fcm_token,
            FCMToken.user_id == current_user_id
        ).first()
        
        if not existing_token:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="FCM 토큰을 찾을 수 없습니다."
            )
        
        success = deactivate_fcm_token(db, fcm_token)
        
        if success:
            return {"message": "FCM 토큰이 비활성화되었습니다."}
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="FCM 토큰 비활성화에 실패했습니다."
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"FCM 토큰 비활성화 실패: {str(e)}"
        )
