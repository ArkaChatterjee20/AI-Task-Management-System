from pydantic import BaseModel


class TaskSummary(BaseModel):
    user_id: int
    total_tasks: int
    completed_tasks: int
    pending_tasks: int
    completion_rate: float


class AnalyticsSummaryResponse(BaseModel):
    total_users: int
    data: list[TaskSummary]