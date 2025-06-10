import sys
from pathlib import Path
from dotenv import load_dotenv

# Определяем путь к .env файлу и загружаем его
env_path = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(env_path)

# Добавляем корневую директорию backend в sys.path для правильного разрешения импортов
backend_root = Path(__file__).resolve().parents[1]
sys.path.append(str(backend_root))

# --- DEBUGGING START ---
print(f"DEBUG: Python executable: {sys.executable}")
print("DEBUG: sys.path contents:")
for p in sys.path:
    print(f"  {p}")
# --- DEBUGGING END ---

from fastapi import FastAPI
# from fastapi_admin.app import app as admin_app
# from fastapi_admin.providers.login import UsernamePasswordProvider

from app.api.api import api_router
from app.core.logging import setup_logging
from app.db.session import engine
from app.db.base import Base
# Импортируем все модели для создания таблиц
from app.models import user

app = FastAPI()


@app.on_event("startup")
async def startup():
    setup_logging()
    # Создаем все таблицы в базе данных
    Base.metadata.create_all(bind=engine)
    # await admin_app.init(
    #     admin_secret="test",
    #     engine=engine,
    #     provider=UsernamePasswordProvider(
    #         admin_model_path="app.admin.Admin",
    #         login_logo_url="https://preview.tabler.io/static/logo-white.svg",
    #     ),
    # )


app.include_router(api_router, prefix="/api/v1")
# app.mount("/admin", admin_app)


@app.get("/")
def read_root():
    return {"Hello": "World"} 