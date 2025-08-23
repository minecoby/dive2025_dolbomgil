from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import logging
from fastapi_limiter import FastAPILimiter
from redis.asyncio import Redis
from contextlib import asynccontextmanager
from db.session import engine
from db.base import Base
from routes.user import router as user_router
from routes.caree import router as caree_router
from routes.location import router as location_router
from routes.safe_zone import router as safe_zone_router
from routes.navigation import router as navigation_router
from routes.pairing import router as pairing_router
from routes.fcm_token import router as fcm_token_router
from routes.home import router as home_router
from utils.key_hash import log_machine_info

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app.log', encoding='utf-8')
    ]
)

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 앱 시작 시 머신 정보 로깅
    machine_hash = log_machine_info()
    logger.info(f"앱 시작 - 머신 해시: {machine_hash}")
    
    # Redis 연결 및 FastAPILimiter 초기화
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6378")
    redis = Redis.from_url(redis_url, encoding="utf-8", decode_responses=True)
    await FastAPILimiter.init(redis)
    logger.info("Redis 연결 및 FastAPILimiter 초기화 완료")
    
    yield
    
    # 앱 종료 시 로깅
    logger.info("앱 종료")

app = FastAPI(lifespan=lifespan)

# 데이터베이스 테이블 생성
Base.metadata.create_all(bind=engine)
logger.info("데이터베이스 테이블 생성 완료")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(user_router)
app.include_router(caree_router)
app.include_router(location_router)
app.include_router(safe_zone_router)
app.include_router(navigation_router)
app.include_router(pairing_router)
app.include_router(fcm_token_router)
app.include_router(home_router)

logger.info("모든 라우터 등록 완료")

if __name__ == "__main__":
    import uvicorn
    logger.info("Uvicorn 서버 시작")
    uvicorn.run("main:app", host="0.0.0.0", port=7777, reload=True)