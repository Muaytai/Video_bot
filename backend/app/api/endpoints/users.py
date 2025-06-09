from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.schemas import user as schemas_user
from app.api import deps
from app.services import user as user_service

router = APIRouter()


@router.post("/", response_model=schemas_user.User)
def create_user(
    *,
    db: Session = Depends(deps.get_db),
    user_in: schemas_user.UserCreate,
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

@router.post("/subscribe")
def subscribe_user(*, db: Session = Depends(deps.get_db), telegram_id: int):
    user = user_service.user.get_by_telegram_id(db, telegram_id=telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user_service.user.update(db, db_obj=user, obj_in={"is_subscribed": True})
    return {"message": "Subscription activated"} 