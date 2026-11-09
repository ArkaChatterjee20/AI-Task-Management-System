
from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Identity,
    String,
    Text,
    UniqueConstraint,
    desc,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from fastapi_backend.database import Base


# =====================================================
# 1. USERS TABLE
# =====================================================

class User(Base):
    __tablename__ = "users"

    __table_args__ = (
        UniqueConstraint("email", name="users_email_key"),
    )

    user_id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(always=True),
        primary_key=True,
    )

    email: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    password_hash: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )


# =====================================================
# 2. TASKS TABLE
# =====================================================

class TaskDB(Base):
    __tablename__ = "tasks"

    __table_args__ = (
        CheckConstraint(
            "LENGTH(TRIM(task_title)) > 0",
            name="chk_task_title",
        ),
        Index(
            "idx_tasks_user_created",
            "user_id",
            desc("created_at"),
            desc("task_id"),
        ),
    )

    task_id: Mapped[int] = mapped_column(
        BigInteger,
        Identity(always=True),
        primary_key=True,
    )

    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
    )

    task_title: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    is_completed: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=func.false(),
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )


# =====================================================
# 3. EXTERNAL TASKS TABLE
# =====================================================

class ExternalTask(Base):
    __tablename__ = "external_tasks"

    __table_args__ = (
        Index(
            "idx_external_tasks_source_user",
            "source_user_id",
        ),
    )

    source_task_id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
    )

    source_user_id: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
    )

    task_title: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    is_completed: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
    )

    imported_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
