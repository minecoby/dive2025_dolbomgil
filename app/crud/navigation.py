import httpx
from typing import Optional, Dict, Any, List
from schema.navigation import NavigationRequest, NavigationError
from utils.config import settings

class NavigationService:
    def __init__(self):
        self.base_url = "https://apis-navi.kakaomobility.com/v1/directions"
        self.walking_base_url = "https://apis-navi.kakaomobility.com/affiliate/walking/v1/directions"
        self.api_key = settings.KAKAO_MOBILITY_API_KEY
        
        print(f"카카오 모빌리티 API 키 설정 상태: {'설정됨' if self.api_key else '설정되지 않음'}")  # 디버깅용 로그
        
        if not self.api_key:
            raise ValueError("KAKAO_MOBILITY_API_KEY 환경변수가 설정되지 않았습니다.")
    
    def process_vertexes(self, vertexes: List[float]) -> List[List[float]]:
        """
        vertexes 배열을 2개씩 묶어서 [경도, 위도] 형태로 변환합니다.
        
        Args:
            vertexes: [경도1, 위도1, 경도2, 위도2, ...] 형태의 배열
            
        Returns:
            [[경도1, 위도1], [경도2, 위도2], ...] 형태의 배열
        """
        if not vertexes or len(vertexes) % 2 != 0:
            return []
        
        processed_vertexes = []
        for i in range(0, len(vertexes), 2):
            if i + 1 < len(vertexes):
                processed_vertexes.append([vertexes[i], vertexes[i + 1]])
        
        return processed_vertexes
    
    def process_sections(self, sections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        sections 데이터의 vertexes를 전처리합니다.
        sections 안에 roads 배열이 있는 경우도 처리합니다.
        """
        if not sections:
            return sections
        
        for section in sections:
            # 직접적인 vertexes 처리
            if 'vertexes' in section and isinstance(section['vertexes'], list):
                section['vertexes'] = self.process_vertexes(section['vertexes'])
            
            # roads 안의 vertexes 처리
            if 'roads' in section and isinstance(section['roads'], list):
                for road in section['roads']:
                    if 'vertexes' in road and isinstance(road['vertexes'], list):
                        road['vertexes'] = self.process_vertexes(road['vertexes'])
        
        return sections
    
    def process_routes(self, routes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        routes 데이터의 sections를 전처리합니다.
        """
        if not routes:
            return routes
        
        for route in routes:
            if 'sections' in route and isinstance(route['sections'], list):
                route['sections'] = self.process_sections(route['sections'])
        
        return routes

    async def get_route(self, request: NavigationRequest) -> Dict[str, Any]:
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
            print(f"카카오 API 요청 URL: {self.base_url}")  # 디버깅용 로그
            print(f"카카오 API 요청 헤더: {headers}")  # 디버깅용 로그
            print(f"카카오 API 요청 파라미터: {params}")  # 디버깅용 로그
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    self.base_url,
                    headers=headers,
                    params=params
                )
                
                print(f"카카오 API 응답 상태 코드: {response.status_code}")  # 디버깅용 로그
                print(f"카카오 API 응답 헤더: {response.headers}")  # 디버깅용 로그
                
                if response.status_code == 200:
                    response_data = response.json()
                    print(f"카카오 API 응답 데이터: {response_data}")  # 디버깅용 로그
                    
                    # 응답 데이터 구조 검증 및 변환
                    try:
                        # 카카오 API 응답 구조에 맞게 데이터 변환
                        if 'routes' in response_data and response_data['routes']:
                            # routes가 비어있지 않은 경우
                            for route in response_data['routes']:
                                if 'sections' in route and route['sections']:
                                    # sections 정보가 있는 경우 distance, duration 계산
                                    total_distance = 0
                                    total_duration = 0
                                    for section in route['sections']:
                                        if 'distance' in section:
                                            total_distance += section.get('distance', 0)
                                        if 'duration' in section:
                                            total_duration += section.get('duration', 0)
                                    
                                    route['distance'] = total_distance
                                    route['duration'] = total_duration
                            
                            # vertexes 전처리만 적용 (응답 구조 변환 제거)
                            if 'routes' in response_data:
                                response_data['routes'] = self.process_routes(response_data['routes'])
                        
                        # 카카오 API 응답을 그대로 반환 (vertexes 전처리만 적용)
                        return response_data
                    except Exception as parse_error:
                        print(f"응답 파싱 오류: {parse_error}")  # 디버깅용 로그
                        print(f"원본 응답 데이터: {response_data}")  # 디버깅용 로그
                        # 파싱 실패 시 원본 데이터로 응답 생성
                        return response_data
                else:
                    try:
                        error_data = response.json()
                        error_msg = error_data.get('message', '알 수 없는 오류')
                        print(f"카카오 API 오류 응답: {error_data}")  # 디버깅용 로그
                    except:
                        error_msg = f"HTTP {response.status_code}: {response.text}"
                        print(f"카카오 API 오류 응답 (JSON 파싱 실패): {response.text}")  # 디버깅용 로그
                    
                    raise NavigationError(
                        error_code=response.status_code,
                        error_msg=f"API 요청 실패: {error_msg}"
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
    
    async def get_walking_route(self, request: NavigationRequest) -> Dict[str, Any]:
        """
        카카오 모빌리티 도보 길찾기 API를 사용하여 보행자 경로를 검색합니다.
        """
        headers = {
            "Authorization": f"KakaoAK {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # 쿼리 파라미터 준비 (도보 API 스펙에 맞게)
        params = {
            "origin": request.origin,
            "destination": request.destination,
            "priority": request.priority.value if request.priority else "DISTANCE",
            "summary": str(request.summary).lower() if request.summary is not None else "false"
        }
        
        # 선택적 파라미터 추가
        if request.waypoints:
            params["waypoints"] = request.waypoints
        
        # default_speed 파라미터 추가 (도보 API 전용)
        if hasattr(request, 'default_speed') and request.default_speed is not None:
            params["default_speed"] = request.default_speed
        
        try:
            print(f"카카오 도보 API 요청 URL: {self.walking_base_url}")  # 디버깅용 로그
            print(f"카카오 도보 API 요청 헤더: {headers}")  # 디버깅용 로그
            print(f"카카오 도보 API 요청 파라미터: {params}")  # 디버깅용 로그
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    self.walking_base_url,
                    headers=headers,
                    params=params
                )
                
                print(f"카카오 도보 API 응답 상태 코드: {response.status_code}")  # 디버깅용 로그
                print(f"카카오 도보 API 응답 헤더: {response.headers}")  # 디버깅용 로그
                
                if response.status_code == 200:
                    response_data = response.json()
                    print(f"카카오 도보 API 응답 데이터: {response_data}")  # 디버깅용 로그
                    
                    # 응답 데이터 구조 검증 및 변환
                    try:
                        # 카카오 도보 API 응답 구조에 맞게 데이터 변환
                        if 'routes' in response_data and response_data['routes']:
                            # routes가 비어있지 않은 경우
                            for route in response_data['routes']:
                                if 'sections' in route and route['sections']:
                                    # sections 정보가 있는 경우 distance, duration 계산
                                    total_distance = 0
                                    total_duration = 0
                                    for section in route['sections']:
                                        if 'distance' in section:
                                            total_distance += section.get('distance', 0)
                                        if 'duration' in section:
                                            total_duration += section.get('duration', 0)
                                    
                                    route['distance'] = total_distance
                                    route['duration'] = total_duration
                            
                            # vertexes 전처리만 적용 (응답 구조 변환 제거)
                            if 'routes' in response_data:
                                response_data['routes'] = self.process_routes(response_data['routes'])
                        
                        # 카카오 API 응답을 그대로 반환 (vertexes 전처리만 적용)
                        return response_data
                    except Exception as parse_error:
                        print(f"응답 파싱 오류: {parse_error}")  # 디버깅용 로그
                        print(f"원본 응답 데이터: {response_data}")  # 디버깅용 로그
                        # 파싱 실패 시 원본 데이터로 응답 생성
                        return response_data
                else:
                    try:
                        error_data = response.json()
                        error_msg = error_data.get('message', '알 수 없는 오류')
                        print(f"카카오 도보 API 오류 응답: {error_data}")  # 디버깅용 로그
                    except:
                        error_msg = f"HTTP {response.status_code}: {response.text}"
                        print(f"카카오 도보 API 오류 응답 (JSON 파싱 실패): {response.text}")  # 디버깅용 로그
                    
                    raise NavigationError(
                        error_code=response.status_code,
                        error_msg=f"도보 API 요청 실패: {error_msg}"
                    )
                    
        except httpx.TimeoutException:
            raise NavigationError(
                error_code=408,
                error_msg="도보 API 요청 시간 초과"
            )
        except httpx.RequestError as e:
            raise NavigationError(
                error_code=500,
                error_msg=f"도보 API 요청 오류: {str(e)}"
            )
        except Exception as e:
            raise NavigationError(
                error_code=500,
                error_msg=f"예상치 못한 오류: {str(e)}"
            )
    
    def format_coordinate(self, x: float, y: float, angle: Optional[int] = None) -> str:
        """
        좌표를 카카오 모빌리티 API 형식으로 변환합니다.
        카카오 API는 경도,위도 순서를 요구합니다.
        """
        # x: 위도(latitude), y: 경도(longitude)
        # 카카오 API 요구사항: 경도,위도 순서
        if angle is not None:
            return f"{y},{x},angle={angle}"
        return f"{y},{x}"
    
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
