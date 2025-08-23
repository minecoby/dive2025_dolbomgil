from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from db.session import get_db
from crud.caree import create_caree, get_carees_by_user, delete_caree_by_user, update_caree
from crud.registration_code import create_registration_code
from schema.caree import CareeCreateRequest, CareeCreateResponse, CareeResponse, CareeDeleteResponse, CareeUpdateRequest
from utils.auth import get_current_user_id

router = APIRouter(prefix="/api/caree", tags=["caree"])


@router.post("/register", response_model=CareeCreateResponse)
async def register_caree(
    caree_data: CareeCreateRequest,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    existing_carees = get_carees_by_user(db, current_user_id)
    if existing_carees:
        return CareeCreateResponse(
            success=False,
            message="이미 등록된 피보호자가 있습니다. 한 계정당 한 명만 등록 가능합니다."
        )
    
    try:
        new_caree = create_caree(db, caree_data, current_user_id)
        
        registration_code = create_registration_code(db, new_caree.caree_id)
        
        return CareeCreateResponse(
            success=True,
            message="피보호자가 성공적으로 등록되었습니다.",
            caree=CareeResponse.from_orm(new_caree),
            registration_code=registration_code
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"피보호자 등록 실패: {str(e)}"
        )


@router.get("/info", response_model=CareeResponse)
async def get_my_caree(
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    try:
        carees = get_carees_by_user(db, current_user_id)
        if not carees:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="등록된 피보호자가 없습니다."
            )
        
        return CareeResponse.from_orm(carees[0])
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"피보호자 정보 조회 실패: {str(e)}"
        )


@router.delete("/delete", response_model=CareeDeleteResponse)
async def delete_my_caree(
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    try:
        success = delete_caree_by_user(db, current_user_id)
        
        if success:
            return CareeDeleteResponse(
                success=True,
                message="피보호자가 성공적으로 삭제되었습니다."
            )
        else:
            return CareeDeleteResponse(
                success=False,
                message="삭제할 피보호자가 없습니다."
            )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"피보호자 삭제 실패: {str(e)}"
        )


@router.put("/update/{caree_id}", response_model=CareeResponse)
async def update_my_caree(
    caree_id: int,
    caree_data: CareeUpdateRequest,
    current_user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    try:
        updated_caree = update_caree(db, caree_id, caree_data, current_user_id)
        
        if not updated_caree:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="수정할 피보호자를 찾을 수 없습니다."
            )
        
        return CareeResponse.from_orm(updated_caree)
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"피보호자 정보 수정 실패: {str(e)}"
        )