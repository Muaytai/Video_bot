from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import schemas
from app.api import deps
from app.services import user as user_service

router = APIRouter()


@router.post("/", response_model=schemas.User)
def create_user(
    *,
    db: Session = Depends(deps.get_db),
    user_in: schemas.UserCreate,
) -> Any:
    """
    Create new user.
    """
    user = user_service.user.get_by_telegram_id(db, telegram_id=user_in.telegram_id)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this telegram id already exists in the system.",
        )
    user = user_service.user.create(db, obj_in=user_in)
    return user 