from typing import Optional

from pydantic import BaseModel


class VideoCreate(BaseModel):
    user_id: int
    theme: str
    chat_id: int
    background: Optional[str] = None
    avatar_info: Optional[str] = None 