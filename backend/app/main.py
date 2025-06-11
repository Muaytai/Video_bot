from fastapi import FastAPI
from app.api.api import api_router
from app.core.config import settings
from app.core.celery_app import celery_app

app = FastAPI(
    title="Video Generation Bot API", openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def read_root():
    return {"Hello": "World"} 