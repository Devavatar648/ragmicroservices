from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import String, Integer, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

class User(Base):

    __tablename__ = "users"

    id: Mapped[str] = mapped_column(
        String(40),
        primary_key=True,
        default=lambda: str(uuid4())
    )

    email : Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False
    )

    password : Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    role : Mapped[str] = mapped_column(
        String(25),
        default='USER'
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )

    total_query : Mapped[int] = mapped_column(
        Integer(),
        default=0
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )

