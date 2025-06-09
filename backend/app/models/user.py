import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime

from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(
        sa.BigInteger, unique=True, index=True
    )
    username: Mapped[str] = mapped_column(sa.String(255), nullable=True)
    first_name: Mapped[str] = mapped_column(sa.String(255), nullable=True)
    last_name: Mapped[str] = mapped_column(sa.String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    is_subscribed: Mapped[bool] = mapped_column(default=False)
    generated_videos_count: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), server_default=sa.func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username='{self.username}')>" 