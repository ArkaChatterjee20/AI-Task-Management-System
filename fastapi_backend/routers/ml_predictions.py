
import logging
import time

from fastapi import APIRouter, HTTPException, Query

from fastapi_backend.ml.feature_loader import iter_task_features
from fastapi_backend.services.prediction_loader import (
    save_predictions_in_batches,
)

from fastapi_backend.services.pipeline_tracker import (
    start_pipeline_run,
    complete_pipeline_run,
    fail_pipeline_run,
)

from fastapi_backend.services.prediction_analytics import (
    get_prediction_summary,
)

from fastapi_backend.services.prediction_history import (
    get_prediction_runs,
    get_prediction_run,
    get_prediction_history_paginated,
)
from pydantic import BaseModel, Field

from fastapi_backend.ml.predictor import (
    predict_tasks_in_batches,
    predict_single_task,
)


router = APIRouter(
    prefix="/ml",
    tags=["ML Predictions"],
)

logger = logging.getLogger(__name__)

BATCH_SIZE = 1000
class SingleTaskPredictionRequest(BaseModel):
    task_title: str = Field(
        min_length=1,
        max_length=500,
        description="Task description to classify",
    )
@router.post("/predict-task")
def predict_single_task_endpoint(
    request: SingleTaskPredictionRequest,
):
    try:
        if not request.task_title.strip():
            raise HTTPException(
                status_code=422,
                detail="Task title cannot be empty.",
            )

        result = predict_single_task(
            request.task_title
        )

        return {
            "status": "success",
            "prediction": result,
        }

    except HTTPException:
        raise

    except Exception:
        logger.exception("Single task prediction failed")

        raise HTTPException(
            status_code=500,
            detail="Could not predict task status",
        )


@router.post("/predictions")
def get_predictions():

    start = time.perf_counter()
    pipeline_run_id = None
    total_predictions = 0

    try:
        # STEP 0: Start pipeline tracking
        pipeline_run_id = start_pipeline_run(
            "ML_TASK_PREDICTION_PIPELINE"
        )

        logger.info(
            "ML pipeline started. RUN_ID: %s",
            pipeline_run_id,
        )

        # STEP 1: Stream features from Snowflake
        logger.info("STEP 1: Loading task features in batches")

        step_start = time.perf_counter()

        feature_batches = iter_task_features(
            batch_size=BATCH_SIZE
        )

        logger.info(
            "STEP 1 completed in %.2f seconds",
            time.perf_counter() - step_start,
        )

        # STEP 2: Generate predictions incrementally
        logger.info("STEP 2: Generating predictions in batches")

        step_start = time.perf_counter()

        prediction_batches = predict_tasks_in_batches(
            feature_batches,
            batch_size=BATCH_SIZE,
        )

        # Count predictions without collecting them in memory.
        def count_prediction_batches():
            nonlocal total_predictions

            for batch in prediction_batches:
                total_predictions += len(batch)

                logger.info(
                    "Generated prediction batch: %s records",
                    len(batch),
                )

                yield batch

        # STEP 3: Save prediction batches to Snowflake
        logger.info("STEP 3: Saving prediction batches")

        step_start = time.perf_counter()

        prediction_run_id = save_predictions_in_batches(
            count_prediction_batches(),
            batch_size=BATCH_SIZE,
        )

        logger.info(
            "STEP 2 completed in %.2f seconds",
            time.perf_counter() - step_start,
        )

        logger.info(
            "Total predictions generated: %s",
            total_predictions,
        )

        # STEP 4: Complete pipeline tracking
        complete_pipeline_run(
            pipeline_run_id,
            total_predictions,
        )

        logger.info(
            "ML pipeline completed successfully. "
            "Prediction RUN_ID: %s",
            prediction_run_id,
        )

        logger.info(
            "Total execution time: %.2f seconds",
            time.perf_counter() - start,
        )

        # Return metadata only.
        # Prediction details are available through paginated history.
        return {
            "run_id": prediction_run_id,
            "pipeline_run_id": pipeline_run_id,
            "status": "SUCCESS",
            "total_predictions": total_predictions,
        }

    except Exception as e:

        logger.exception("Prediction pipeline failed")

        if pipeline_run_id is not None:
            try:
                fail_pipeline_run(
                    pipeline_run_id,
                    str(e)[:500],
                )

            except Exception:
                logger.exception(
                    "Could not update pipeline failure status"
                )

        raise HTTPException(
            status_code=500,
            detail="Prediction pipeline failed",
        )


@router.get("/analytics")
def get_ml_analytics():

    try:
        summary = get_prediction_summary()

        return {
            "status": "success",
            "analytics": summary,
        }

    except Exception:
        logger.exception("ML analytics retrieval failed")

        raise HTTPException(
            status_code=500,
            detail="Could not retrieve ML analytics",
        )


@router.get("/prediction-runs")
def prediction_runs(
    limit: int = Query(default=20, ge=1, le=500),
):

    try:
        runs = get_prediction_runs(limit)

        return {
            "total_runs": len(runs),
            "runs": runs,
        }

    except Exception:
        logger.exception("Prediction runs retrieval failed")

        raise HTTPException(
            status_code=500,
            detail="Could not retrieve prediction runs",
        )


@router.get("/prediction-runs/{run_id}")
def prediction_run_details(run_id: str):

    try:
        run = get_prediction_run(run_id)

        if run is None:
            raise HTTPException(
                status_code=404,
                detail="Prediction run not found",
            )

        return run

    except HTTPException:
        raise

    except Exception:
        logger.exception("Prediction run retrieval failed")

        raise HTTPException(
            status_code=500,
            detail="Could not retrieve prediction run",
        )


@router.get("/prediction-runs/{run_id}/history")
def prediction_run_history(
    run_id: str,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=100, ge=1, le=1000),
):

    try:
        history = get_prediction_history_paginated(
            run_id=run_id,
            page=page,
            page_size=page_size,
        )

        return {
            "run_id": run_id,
            **history,
        }

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

    except Exception:
        logger.exception("Prediction history retrieval failed")

        raise HTTPException(
            status_code=500,
            detail="Could not retrieve prediction history",
        )
