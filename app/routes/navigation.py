from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from schema.navigation import NavigationRequest, NavigationResponse, NavigationError, PriorityEnum, CarFuelEnum
from crud.navigation import NavigationService
from utils.auth import get_current_user
from models.user import User
from typing import Optional

router = APIRouter(prefix="/navigation", tags=["navigation"])

@router.get("/route", response_model=NavigationResponse)
async def get_route(
    origin: str,
    destination: str,
    waypoints: Optional[str] = None,
    priority: Optional[PriorityEnum] = PriorityEnum.RECOMMEND,
    summary: Optional[bool] = True,
    alternatives: Optional[bool] = False,
    road_details: Optional[bool] = False,
    car_fuel: Optional[CarFuelEnum] = CarFuelEnum.GASOLINE,
    car_hipass: Optional[bool] = False,
    current_user: Optional[User] = Depends(get_current_user)
):
    """
    출발지에서 목적지까지의 자동차 경로를 검색합니다.
    
    - **origin**: 출발지 좌표 (예: 127.111202,37.394912,angle=270)
    - **destination**: 목적지 좌표 (예: 127.111202,37.394912)
    - **waypoints**: 경유지 좌표 (선택사항)
    - **priority**: 경로 탐색 우선순위 (RECOMMEND, TIME, DISTANCE)
    - **summary**: 경로 요약 정보 제공 여부
    - **alternatives**: 대안 경로 제공 여부
    - **road_details**: 상세 도로 정보 제공 여부
    - **car_fuel**: 차량 유종 (GASOLINE, DIESEL, LPG)
    - **car_hipass**: 하이패스 사용 여부
    """
    try:
        navigation_service = NavigationService()
        
        # NavigationRequest 객체 생성
        request = NavigationRequest(
            origin=origin,
            destination=destination,
            waypoints=waypoints,
            priority=priority,
            summary=summary,
            alternatives=alternatives,
            road_details=road_details,
            car_fuel=car_fuel,
            car_hipass=car_hipass
        )
        
        result = await navigation_service.get_route(request)
        return result
        
    except NavigationError as e:
        raise HTTPException(
            status_code=e.error_code,
            detail=e.error_msg
        )
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"서버 내부 오류: {str(e)}"
        )

@router.get("/route/simple")
async def get_simple_route(
    origin_x: float,
    origin_y: float,
    destination_x: float,
    destination_y: float,
    angle: Optional[int] = None,
    current_user: Optional[User] = Depends(get_current_user)
):
    """
    간단한 좌표 기반 경로 검색
    """
    try:
        navigation_service = NavigationService()
        
        # 좌표 형식 변환
        origin = navigation_service.format_coordinate(origin_x, origin_y, angle)
        destination = navigation_service.format_coordinate(destination_x, destination_y)
        
        # 기본 요청 생성
        request = NavigationRequest(
            origin=origin,
            destination=destination
        )
        
        result = await navigation_service.get_route(request)
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"경로 검색 실패: {str(e)}"
        )


        
