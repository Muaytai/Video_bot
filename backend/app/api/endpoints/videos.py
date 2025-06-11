from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.video import VideoCreate
from app.api import deps
from app.tasks.video_generation import generate_video_task
from app.services import user as user_service
from app.core.config import settings

router = APIRouter()


@router.post("/")
def create_video(
    *,
    db: Session = Depends(deps.get_db),
    video_in: VideoCreate,
):
    """
    Create new video generation task.
    """
    user = user_service.user.get_by_telegram_id(db, telegram_id=video_in.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.generated_videos_count >= 5 and not user.is_subscribed:
        raise HTTPException(
            status_code=403,
            detail="You have reached the limit of free videos.",
        )

    task = generate_video_task.delay(
        video_in.user_id,
        video_in.theme,
        video_in.chat_id,
        video_in.background,
        video_in.avatar_info,
    )

    if not user.is_subscribed:
        user_service.user.update(
            db,
            db_obj=user,
            obj_in={"generated_videos_count": user.generated_videos_count + 1},
        )

    return {"message": "Video generation started", "task_id": task.id} 