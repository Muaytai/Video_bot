from fastapi import APIRouter

from app.api.endpoints import users, videos

api_router = APIRouter()
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(videos.router, prefix="/videos", tags=["videos"]) 