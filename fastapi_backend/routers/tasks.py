from fastapi import APIRouter, HTTPException

from fastapi_backend.services.snowflake_service import (
    get_all_tasks,
    get_task_by_id,
)
from fastapi_backend.models.task import (
    Task,
    TaskListResponse,
)


router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"],
)


@router.get("/", response_model=TaskListResponse)
def get_tasks():
    """
    Return all tasks.
    """

    tasks = get_all_tasks()

    return {
        "total_tasks": len(tasks),
        "data": tasks,
    }


@router.get("/{task_id}", response_model=Task)
def get_single_task(task_id: int):
    """
    Return one task by ID.
    """

    task = get_task_by_id(task_id)

    if task is None:
        raise HTTPException(
            status_code=404,
            detail=f"Task with ID {task_id} was not found.",
        )

    return task