from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from schema.navigation import NavigationRequest, NavigationResponse, NavigationError, PriorityEnum, CarFuelEnum, WalkingNavigationRequest, WalkingPriorityEnum
from crud.navigation import NavigationService
from crud.location import get_latest_protector_location, get_latest_caree_location
from crud.caree import get_carees_by_user
from utils.auth import get_current_user
from models.user import User
from models.position_history import PositionHistory
from db.session import get_db
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any

router = APIRouter(prefix="/navigation", tags=["navigation"])

@router.get("/route")
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
        # 카카오 API 응답을 그대로 반환 (vertexes 전처리만 적용됨)
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
        print(f"예상치 못한 오류 발생: {str(e)}")  # 디버깅용 로그
        print(f"오류 타입: {type(e)}")  # 디버깅용 로그
        import traceback
        print(f"스택 트레이스: {traceback.format_exc()}")  # 디버깅용 로그
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

@router.get("/route/protector-to-caree")
async def get_protector_to_caree_route(
    priority: Optional[PriorityEnum] = PriorityEnum.RECOMMEND,
    summary: Optional[bool] = True,
    alternatives: Optional[bool] = False,
    road_details: Optional[bool] = False,
    car_fuel: Optional[CarFuelEnum] = CarFuelEnum.GASOLINE,
    car_hipass: Optional[bool] = False,
    current_user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    보호자의 현재 위치에서 피보호자의 현재 위치까지의 경로를 검색합니다.
    
    - **priority**: 경로 탐색 우선순위 (RECOMMEND, TIME, DISTANCE)
    - **summary**: 경로 요약 정보 제공 여부
    - **alternatives**: 대안 경로 제공 여부
    - **road_details**: 상세 도로 정보 제공 여부
    - **car_fuel**: 차량 유종 (GASOLINE, DIESEL, LPG)
    - **car_hipass**: 하이패스 사용 여부
    """
    try:
        # 현재 보호자의 피보호자 조회
        carees = get_carees_by_user(db, current_user.user_id)
        if not carees:
            raise HTTPException(
                status_code=404,
                detail="등록된 피보호자가 없습니다."
            )
        
        caree_id = carees[0].caree_id
        
        # 보호자와 피보호자의 최신 위치 정보 조회
        protector_location = get_latest_protector_location(db, current_user.user_id)
        caree_location = get_latest_caree_location(db, caree_id)
        
        print(f"보호자 위치: {protector_location}")  # 디버깅용 로그
        print(f"피보호자 위치: {caree_location}")    # 디버깅용 로그
        
        if not protector_location:
            raise HTTPException(
                status_code=404,
                detail="보호자의 위치 정보를 찾을 수 없습니다."
            )
        
        if not caree_location:
            raise HTTPException(
                status_code=404,
                detail="피보호자의 위치 정보를 찾을 수 없습니다."
            )
        
        navigation_service = NavigationService()
        
        # 좌표 형식 변환 (보호자 위치에 각도 정보 포함)
        print(f"보호자 원본 좌표 - 위도: {protector_location.latitude}, 경도: {protector_location.longitude}")
        print(f"피보호자 원본 좌표 - 위도: {caree_location.latitude}, 경도: {caree_location.longitude}")
        
        origin = navigation_service.format_coordinate(
            protector_location.latitude, 
            protector_location.longitude, 
            None  # 각도 정보가 있다면 추가 가능
        )
        destination = navigation_service.format_coordinate(
            caree_location.latitude, 
            caree_location.longitude
        )
        
        print(f"변환된 출발지 좌표: {origin}")      # 디버깅용 로그
        print(f"변환된 목적지 좌표: {destination}") # 디버깅용 로그
        
        # NavigationRequest 객체 생성
        request = NavigationRequest(
            origin=origin,
            destination=destination,
            priority=priority,
            summary=summary,
            alternatives=alternatives,
            road_details=road_details,
            car_fuel=car_fuel,
            car_hipass=car_hipass
        )
        
        print(f"NavigationRequest: {request}")  # 디버깅용 로그
        
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

@router.get("/walking/route")
async def get_walking_route(
    origin: str,
    destination: str,
    waypoints: Optional[str] = None,
    priority: Optional[WalkingPriorityEnum] = WalkingPriorityEnum.DISTANCE,
    summary: Optional[bool] = False,
    default_speed: Optional[float] = 0,
    current_user: Optional[User] = Depends(get_current_user)
):
    """
    출발지에서 목적지까지의 도보 경로를 검색합니다.
    
    - **origin**: 출발지 좌표 (예: 127.111202,37.394912)
    - **destination**: 목적지 좌표 (예: 127.111202,37.394912)
    - **waypoints**: 경유지 좌표 (선택사항, 최대 5개)
    - **priority**: 경로 탐색 우선순위 (DISTANCE, MAIN_STREET)
    - **summary**: 경로 요약 정보 제공 여부
    - **default_speed**: 도보 속도 (km/h, 기본값: 4km/h)
    """
    try:
        navigation_service = NavigationService()
        
        # WalkingNavigationRequest 객체 생성
        request = WalkingNavigationRequest(
            origin=origin,
            destination=destination,
            waypoints=waypoints,
            priority=priority,
            summary=summary,
            default_speed=default_speed
        )
        
        result = await navigation_service.get_walking_route(request)
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
        print(f"예상치 못한 오류 발생: {str(e)}")  # 디버깅용 로그
        print(f"오류 타입: {type(e)}")  # 디버깅용 로그
        import traceback
        print(f"스택 트레이스: {traceback.format_exc()}")  # 디버깅용 로그
        raise HTTPException(
            status_code=500,
            detail=f"서버 내부 오류: {str(e)}"
        )

@router.get("/walking/route/simple")
async def get_simple_walking_route(
    origin_x: float,
    origin_y: float,
    destination_x: float,
    destination_y: float,
    priority: Optional[WalkingPriorityEnum] = WalkingPriorityEnum.DISTANCE,
    summary: Optional[bool] = False,
    default_speed: Optional[float] = 0,
    current_user: Optional[User] = Depends(get_current_user)
):
    """
    간단한 좌표 기반 도보 경로 검색
    """
    try:
        navigation_service = NavigationService()
        
        # 좌표 형식 변환
        origin = navigation_service.format_coordinate(origin_x, origin_y)
        destination = navigation_service.format_coordinate(destination_x, destination_y)
        
        # 기본 요청 생성
        request = WalkingNavigationRequest(
            origin=origin,
            destination=destination,
            priority=priority,
            summary=summary,
            default_speed=default_speed
        )
        
        result = await navigation_service.get_walking_route(request)
        return result
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"도보 경로 검색 실패: {str(e)}"
        )

@router.get("/walking/route/protector-to-caree")
async def get_protector_to_caree_walking_route(
    priority: Optional[WalkingPriorityEnum] = WalkingPriorityEnum.DISTANCE,
    summary: Optional[bool] = False,
    default_speed: Optional[float] = 0,
    current_user: Optional[User] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    보호자의 현재 위치에서 피보호자의 현재 위치까지의 도보 경로를 검색합니다.
    
    - **priority**: 경로 탐색 우선순위 (DISTANCE, MAIN_STREET)
    - **summary**: 경로 요약 정보 제공 여부
    - **default_speed**: 도보 속도 (km/h, 기본값: 4km/h)
    """
    try:
        # 현재 보호자의 피보호자 조회
        carees = get_carees_by_user(db, current_user.user_id)
        if not carees:
            raise HTTPException(
                status_code=404,
                detail="등록된 피보호자가 없습니다."
            )
        
        caree_id = carees[0].caree_id
        
        # 보호자와 피보호자의 최신 위치 정보 조회
        protector_location = get_latest_protector_location(db, current_user.user_id)
        caree_location = get_latest_caree_location(db, caree_id)
        
        print(f"보호자 위치: {protector_location}")  # 디버깅용 로그
        print(f"피보호자 위치: {caree_location}")    # 디버깅용 로그
        
        if not protector_location:
            raise HTTPException(
                status_code=404,
                detail="보호자의 위치 정보를 찾을 수 없습니다."
            )
        
        if not caree_location:
            raise HTTPException(
                status_code=404,
                detail="피보호자의 위치 정보를 찾을 수 없습니다."
            )
        
        navigation_service = NavigationService()
        
        # 좌표 형식 변환
        print(f"보호자 원본 좌표 - 위도: {protector_location.latitude}, 경도: {protector_location.longitude}")
        print(f"피보호자 원본 좌표 - 위도: {caree_location.latitude}, 경도: {caree_location.longitude}")
        
        origin = navigation_service.format_coordinate(
            protector_location.latitude, 
            protector_location.longitude
        )
        destination = navigation_service.format_coordinate(
            caree_location.latitude, 
            caree_location.longitude
        )
        
        print(f"변환된 출발지 좌표: {origin}")      # 디버깅용 로그
        print(f"변환된 목적지 좌표: {destination}") # 디버깅용 로그
        
        # WalkingNavigationRequest 객체 생성
        request = WalkingNavigationRequest(
            origin=origin,
            destination=destination,
            priority=priority,
            summary=summary,
            default_speed=default_speed
        )
        
        print(f"WalkingNavigationRequest: {request}")  # 디버깅용 로그
        
        result = await navigation_service.get_walking_route(request)
        #print(f"도보 경로 검색 결과: {result}")  # 디버깅용 로그
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


        
