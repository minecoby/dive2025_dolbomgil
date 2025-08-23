from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum

class PriorityEnum(str, Enum):
    RECOMMEND = "RECOMMEND"
    TIME = "TIME"
    DISTANCE = "DISTANCE"

class WalkingPriorityEnum(str, Enum):
    DISTANCE = "DISTANCE"
    MAIN_STREET = "MAIN_STREET"

class CarFuelEnum(str, Enum):
    GASOLINE = "GASOLINE"
    DIESEL = "DIESEL"
    LPG = "LPG"

class NavigationRequest(BaseModel):
    origin: str = Field(..., description="출발지 좌표 (예: 127.111202,37.394912,angle=270)")
    destination: str = Field(..., description="목적지 좌표 (예: 127.111202,37.394912)")
    waypoints: Optional[str] = Field(default=None, description="경유지 좌표 (예: 127.17354989857544,37.36629687436494)")
    priority: Optional[PriorityEnum] = Field(default=PriorityEnum.RECOMMEND, description="경로 탐색 우선순위")
    summary: Optional[bool] = Field(default=True, description="경로 요약 정보 제공 여부")
    alternatives: Optional[bool] = Field(default=False, description="대안 경로 제공 여부")
    road_details: Optional[bool] = Field(default=False, description="상세 도로 정보 제공 여부")
    car_fuel: Optional[CarFuelEnum] = Field(default=CarFuelEnum.GASOLINE, description="차량 유종")
    car_hipass: Optional[bool] = Field(default=False, description="하이패스 사용 여부")

class WalkingNavigationRequest(BaseModel):
    origin: str = Field(..., description="출발지 좌표 (예: 127.111202,37.394912)")
    destination: str = Field(..., description="목적지 좌표 (예: 127.111202,37.394912)")
    waypoints: Optional[str] = Field(default=None, description="경유지 좌표 (예: 127.17354989857544,37.36629687436494)")
    priority: Optional[WalkingPriorityEnum] = Field(default=WalkingPriorityEnum.DISTANCE, description="경로 탐색 우선순위")
    summary: Optional[bool] = Field(default=False, description="경로 요약 정보 제공 여부")
    default_speed: Optional[float] = Field(default=0, description="도보 속도 (km/h, 기본값: 4km/h)")

class Coordinate(BaseModel):
    name: str
    x: float
    y: float

class Bound(BaseModel):
    min_x: float
    min_y: float
    max_x: float
    max_y: float

class Fare(BaseModel):
    taxi: int
    toll: int

class Road(BaseModel):
    name: str
    distance: int
    duration: int
    traffic_speed: Optional[float] = None
    traffic_state: Optional[int] = None
    vertexes: Optional[List[float]] = None

class Section(BaseModel):
    distance: int
    duration: int
    bound: Optional[Bound] = None
    roads: Optional[List[Road]] = None

class Guide(BaseModel):
    name: str
    x: float
    y: float
    distance: int
    duration: int
    type: int
    guidance: str
    road_index: int

class Summary(BaseModel):
    origin: Coordinate
    destination: Coordinate
    waypoints: List[Coordinate]
    priority: Optional[str] = None
    bound: Optional[Bound] = None
    fare: Optional[Fare] = None
    distance: Optional[int] = None
    duration: Optional[int] = None

class Route(BaseModel):
    result_code: Optional[int] = None
    result_msg: Optional[str] = None
    summary: Optional[Summary] = None
    bound: Optional[Bound] = None
    fare: Optional[Fare] = None
    distance: Optional[int] = None
    duration: Optional[int] = None
    sections: Optional[List[Section]] = None
    guides: Optional[List[Guide]] = None

class NavigationResponse(BaseModel):
    trans_id: Optional[str] = None
    routes: Optional[List[Route]] = None
    # 카카오 모빌리티 API 실제 응답 필드들
    result_code: Optional[int] = None
    result_msg: Optional[str] = None
    summary: Optional[Summary] = None
    priority: Optional[str] = None
    # 추가 필드들
    code: Optional[int] = None
    message: Optional[str] = None
    
    class Config:
        extra = "allow"  # 추가 필드 허용

class NavigationError(Exception):
    def __init__(self, error_code: int, error_msg: str):
        self.error_code = error_code
        self.error_msg = error_msg
        super().__init__(error_msg)
