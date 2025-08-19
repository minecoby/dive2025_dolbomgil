from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
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

@asynccontextmanager
async def lifespan(app: FastAPI):
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6378")
    redis = Redis.from_url(redis_url, encoding="utf-8", decode_responses=True)
    await FastAPILimiter.init(redis)
    yield

app = FastAPI(lifespan=lifespan)
Base.metadata.create_all(bind=engine)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_router)
app.include_router(caree_router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=7777, reload=True)