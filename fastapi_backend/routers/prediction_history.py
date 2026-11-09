from fastapi import APIRouter, HTTPException, Query

from fastapi_backend.services.prediction_history import (
    get_recent_predictions
)

router = APIRouter(
    prefix="/ml",
    tags=["Prediction History"]
)


@router.get("/recent-predictions")
def recent_predictions(
    limit: int = Query(default=100, ge=1, le=1000)
):

    try:
        history = get_recent_predictions(limit)

        return {
            "total_records": len(history),
            "predictions": history
        }

    except Exception as e:

        print("Prediction history error:", str(e))

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )