from fastapi import APIRouter

from fastapi_backend.services.snowflake_service import (
    get_task_summary,
)
from fastapi_backend.models.analytics import (
    AnalyticsSummaryResponse,
)


router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"],
)

@router.get(
    "/summary",
    response_model=AnalyticsSummaryResponse,
)
def get_analytics_summary():
    """
    Return task analytics summary from Snowflake.
    """

    summary = get_task_summary()

    return {
        "total_users": len(summary),
        "data": summary,
    }