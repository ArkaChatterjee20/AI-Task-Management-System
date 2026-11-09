from datetime import datetime
from pydantic import BaseModel


class Task(BaseModel):
    task_id: int
    user_id: int
    task_title: str
    completion_status: str
    is_completed: bool
    extracted_at: datetime


class TaskListResponse(BaseModel):
    total_tasks: int
    data: list[Task]