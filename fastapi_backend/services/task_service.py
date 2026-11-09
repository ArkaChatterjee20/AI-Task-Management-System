
from datetime import datetime, timezone

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from fastapi_backend.db_models import TaskDB


# =====================================================
# 1. CREATE TASK
# =====================================================

def create_task(
    db: Session,
    user_id: int,
    task_title: str,
):
    new_task = TaskDB(
        user_id=user_id,
        task_title=task_title.strip(),
    )

    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    return new_task


# =====================================================
# 2. GET USER TASKS WITH PAGINATION
# =====================================================

def get_user_tasks(
    db: Session,
    user_id: int,
    page: int = 1,
    page_size: int = 20,
):
    total_tasks = db.scalar(
        select(func.count())
        .select_from(TaskDB)
        .where(TaskDB.user_id == user_id)
    )

    offset = (page - 1) * page_size

    query = (
        select(TaskDB)
        .where(TaskDB.user_id == user_id)
        .order_by(
            TaskDB.created_at.desc(),
            TaskDB.task_id.desc(),
        )
        .offset(offset)
        .limit(page_size)
    )

    tasks = db.scalars(query).all()

    return {
        "total_tasks": total_tasks or 0,
        "page": page,
        "page_size": page_size,
        "data": tasks,
    }


# =====================================================
# 3. GET SINGLE USER TASK
# =====================================================

def get_user_task(
    db: Session,
    user_id: int,
    task_id: int,
):
    query = select(TaskDB).where(
        TaskDB.task_id == task_id,
        TaskDB.user_id == user_id,
    )

    return db.scalar(query)


# =====================================================
# 4. UPDATE USER TASK
# =====================================================

def update_task(
    db: Session,
    task: TaskDB,
    updates: dict,
):
    if "task_title" in updates and updates["task_title"] is not None:
        task.task_title = updates["task_title"].strip()

    if "is_completed" in updates and updates["is_completed"] is not None:
        task.is_completed = updates["is_completed"]

    task.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(task)

    return task


# =====================================================
# 5. DELETE USER TASK
# =====================================================

def delete_task(
    db: Session,
    task: TaskDB,
):
    db.delete(task)
    db.commit()

    return True
