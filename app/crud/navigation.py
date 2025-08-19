import httpx
from typing import Optional, Dict, Any
from schema.navigation import NavigationRequest, NavigationResponse, NavigationError
from utils.config import settings

class NavigationService:
    def __init__(self):
        self.base_url = "https://apis-navi.kakaomobility.com/v1/directions"
        self.api_key = settings.KAKAO_MOBILITY_API_KEY
        
        if not self.api_key:
            raise ValueError("KAKAO_MOBILITY_API_KEY 환경변수가 설정되지 않았습니다.")
    
    async def get_route(self, request: NavigationRequest) -> NavigationResponse:
        """
        카카오 모빌리티 API를 사용하여 경로를 검색합니다.
        """
        headers = {
            "Authorization": f"KakaoAK {self.api_key}"
        }
        
        # 쿼리 파라미터 준비
        params = {
            "origin": request.origin,
            "destination": request.destination,
            "priority": request.priority.value if request.priority else "RECOMMEND",
            "summary": str(request.summary).lower() if request.summary is not None else "true",
            "alternatives": str(request.alternatives).lower() if request.alternatives is not None else "false",
            "road_details": str(request.road_details).lower() if request.road_details is not None else "false",
            "car_fuel": request.car_fuel.value if request.car_fuel else "GASOLINE",
            "car_hipass": str(request.car_hipass).lower() if request.car_hipass is not None else "false"
        }
        
        # 선택적 파라미터 추가
        if request.waypoints:
            params["waypoints"] = request.waypoints
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    self.base_url,
                    headers=headers,
                    params=params
                )
                
                if response.status_code == 200:
                    response_data = response.json()
                    print(f"카카오 API 응답: {response_data}")  # 디버깅용 로그
                    return NavigationResponse(**response_data)
                else:
                    error_data = response.json()
                    raise NavigationError(
                        error_code=response.status_code,
                        error_msg=f"API 요청 실패: {error_data.get('message', '알 수 없는 오류')}"
                    )
                    
        except httpx.TimeoutException:
            raise NavigationError(
                error_code=408,
                error_msg="API 요청 시간 초과"
            )
        except httpx.RequestError as e:
            raise NavigationError(
                error_code=500,
                error_msg=f"API 요청 오류: {str(e)}"
            )
        except Exception as e:
            raise NavigationError(
                error_code=500,
                error_msg=f"예상치 못한 오류: {str(e)}"
            )
    
    def format_coordinate(self, x: float, y: float, angle: Optional[int] = None) -> str:
        """
        좌표를 카카오 모빌리티 API 형식으로 변환합니다.
        """
        if angle is not None:
            return f"{x},{y},angle={angle}"
        return f"{x},{y}"
    
    def parse_coordinate(self, coordinate_str: str) -> Dict[str, Any]:
        """
        카카오 모빌리티 API 좌표 문자열을 파싱합니다.
        """
        parts = coordinate_str.split(',')
        result = {}
        
        if len(parts) >= 2:
            result['x'] = float(parts[0])
            result['y'] = float(parts[1])
            
            # 추가 정보 파싱
            for part in parts[2:]:
                if '=' in part:
                    key, value = part.split('=', 1)
                    result[key.strip()] = value.strip()
        
        return result
