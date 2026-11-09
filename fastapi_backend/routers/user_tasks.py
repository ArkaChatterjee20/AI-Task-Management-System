
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
)
from sqlalchemy.orm import Session

from fastapi_backend.database import get_db
from fastapi_backend.db_models import User
from fastapi_backend.models.task_crud import (
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    TaskListResponse,
)
from fastapi_backend.routers.auth import get_current_user
from fastapi_backend.services.task_service import (
    create_task,
    get_user_tasks,
    get_user_task,
    update_task,
    delete_task,
)


router = APIRouter(
    prefix="/user-tasks",
    tags=["User Task Management"],
)


# =====================================================
# 1. CREATE TASK
# =====================================================

@router.post(
    "/",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_user_task(
    task_data: TaskCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return create_task(
        db=db,
        user_id=current_user.user_id,
        task_title=task_data.task_title,
    )


# =====================================================
# 2. GET USER TASKS WITH PAGINATION
# =====================================================

@router.get(
    "/",
    response_model=TaskListResponse,
)
def list_user_tasks(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_user_tasks(
        db=db,
        user_id=current_user.user_id,
        page=page,
        page_size=page_size,
    )


# =====================================================
# 3. GET SINGLE TASK
# =====================================================

@router.get(
    "/{task_id}",
    response_model=TaskResponse,
)
def retrieve_user_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = get_user_task(
        db=db,
        user_id=current_user.user_id,
        task_id=task_id,
    )

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    return task


# =====================================================
# 4. UPDATE TASK
# =====================================================

@router.patch(
    "/{task_id}",
    response_model=TaskResponse,
)
def modify_user_task(
    task_id: int,
    task_data: TaskUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = get_user_task(
        db=db,
        user_id=current_user.user_id,
        task_id=task_id,
    )

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    updates = task_data.model_dump(exclude_unset=True)

    if not updates:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Provide at least one field to update",
        )

    if (
        "task_title" in updates
        and updates["task_title"] is not None
        and not updates["task_title"].strip()
    ):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Task title cannot be empty",
        )

    return update_task(
        db=db,
        task=task,
        updates=updates,
    )


# =====================================================
# 5. DELETE TASK
# =====================================================

@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_user_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = get_user_task(
        db=db,
        user_id=current_user.user_id,
        task_id=task_id,
    )

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found",
        )

    delete_task(db=db, task=task)

    return None
