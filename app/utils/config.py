import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

class Settings:
    # 카카오 모빌리티 API
    KAKAO_MOBILITY_API_KEY: str = os.getenv("KAKAO_MOBILITY_API_KEY", "")
    
    # 데이터베이스
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    
    # JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "")
    
    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6378")

settings = Settings()
