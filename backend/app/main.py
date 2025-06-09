import sys
from pathlib import Path

# Добавляем корневую директорию проекта в sys.path
# Это решает проблемы с импортами вида "from app.models..."
# .. -> app -> backend -> project_root
project_root = Path(__file__).resolve().parents[2]
sys.path.append(str(project_root))

from fastapi import FastAPI
from fastapi_admin.app import app as admin_app
from fastapi_admin.providers.login import UsernamePasswordProvider

from app.api.api import api_router
from app.core.logging import setup_logging
from app.db.session import engine

app = FastAPI()


@app.on_event("startup")
async def startup():
    setup_logging()
    await admin_app.init(
        admin_secret="test",
        engine=engine,
        provider=UsernamePasswordProvider(
            admin_model_path="app.admin.Admin",
            login_logo_url="https://preview.tabler.io/static/logo-white.svg",
        ),
    )


app.include_router(api_router, prefix="/api/v1")
app.mount("/admin", admin_app)


@app.get("/")
def read_root():
    return {"Hello": "World"} 