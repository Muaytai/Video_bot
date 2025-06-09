from typing import Optional

from pydantic import BaseModel


# Shared properties
class UserBase(BaseModel):
    telegram_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None


# Properties to receive on user creation
class UserCreate(UserBase):
    pass


# Properties to receive on user update
class UserUpdate(UserBase):
    pass


# Properties shared by models stored in DB
class UserInDBBase(UserBase):
    id: int
    is_active: bool
    is_subscribed: bool
    generated_videos_count: int

    class Config:
        orm_mode = True


# Properties to return to client
class User(UserInDBBase):
    pass


# Properties properties stored in DB
class UserInDB(UserInDBBase):
    pass 