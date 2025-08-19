from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from db.session import get_db
from crud.pairing import pair_watch_with_caree
from schema.pairing import WatchPairingRequest, WatchPairingResponse

router = APIRouter(prefix="/api/pairing", tags=["pairing"])


@router.post("/connect", response_model=WatchPairingResponse)
async def pair_watch(
    pairing_data: WatchPairingRequest,
    db: Session = Depends(get_db)
):
    """워치와 피보호자 페어링"""
    try:
        caree = pair_watch_with_caree(db, pairing_data)
        
        if not caree:
            return WatchPairingResponse(
                success=False,
                message="유효하지 않은 등록코드이거나 이미 페어링된 피보호자입니다."
            )
        
        return WatchPairingResponse(
            success=True,
            message=f"{caree.name}님과 성공적으로 연결되었습니다.",
            caree_name=caree.name,
            caree_id=caree.caree_id
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"워치 페어링 실패: {str(e)}"
        )