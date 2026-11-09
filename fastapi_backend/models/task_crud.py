
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


# Request schema for creating a task
class TaskCreate(BaseModel):
    task_title: str = Field(min_length=1, max_length=500)


# Request schema for updating a task
class TaskUpdate(BaseModel):
    task_title: str | None = Field(
        default=None,
        min_length=1,
        max_length=500,
    )
    is_completed: bool | None = None


# Response schema for PostgreSQL tasks
class TaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    task_id: int
    user_id: int
    task_title: str
    is_completed: bool
    created_at: datetime
    updated_at: datetime


# Response schema for paginated tasks
class TaskListResponse(BaseModel):
    total_tasks: int
    page: int
    page_size: int
    data: list[TaskResponse]
