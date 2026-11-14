
import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from api_elt_pipeline.main import main as run_elt_pipeline

from fastapi_backend.database import get_db
from fastapi_backend.services.elt_tracking_service import (
    create_pipeline_run,
    complete_pipeline_run,
    fail_pipeline_run,
    get_pipeline_runs,
    get_pipeline_run_by_id,
)

router = APIRouter(
    prefix="/pipeline",
    tags=["Pipeline"],
)

# =====================================================
# EXECUTE ELT PIPELINE
# =====================================================

@router.post("/run")
def run_pipeline(db: Session = Depends(get_db)):
    """
    Execute the ELT pipeline and persist execution metrics
    in PostgreSQL.
    """

    pipeline_run = None

    try:
        logging.info(
            "Pipeline execution requested through FastAPI."
        )

        # STEP 1: Create RUNNING execution record.
        pipeline_run = create_pipeline_run(db)

        logging.info(
            "Pipeline tracking started. Execution ID: %s",
            pipeline_run.id,
        )

        # STEP 2: Execute the existing ELT pipeline.
        result = run_elt_pipeline()

        # STEP 3: Persist execution results.
        pipeline_run = complete_pipeline_run(
            db=db,
            run=pipeline_run,
            result=result,
        )

        logging.info(
            "Pipeline execution recorded. ID: %s | Status: %s",
            pipeline_run.id,
            pipeline_run.status,
        )

        if result["status"] == "NO_NEW_RECORDS":
            message = "No new records available for processing."
        else:
            message = "ELT pipeline completed successfully."

        return {
            **result,
            "execution_id": pipeline_run.id,
            "execution_duration_seconds": (
                pipeline_run.duration_seconds
            ),
            "message": message,
        }

    except Exception as error:

        logging.exception(
            "ELT pipeline execution failed: %s",
            error,
        )

        # Roll back any incomplete database transaction.
        db.rollback()

        # Persist the failed execution.
        if pipeline_run is not None:
            try:
                fail_pipeline_run(
                    db=db,
                    run=pipeline_run,
                    error_message=str(error),
                )

            except Exception:
                db.rollback()

                logging.exception(
                    "Could not persist pipeline failure."
                )

        raise HTTPException(
            status_code=500,
            detail="ELT pipeline execution failed.",
        )





# =====================================================
# PIPELINE EXECUTION HISTORY
# =====================================================

@router.get("/runs")
def list_pipeline_runs(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    """
    Retrieve paginated ELT pipeline execution history.
    """

    try:
        return {
            "status": "success",
            **get_pipeline_runs(
                db=db,
                limit=limit,
                offset=offset,
            ),
        }

    except Exception:
        logging.exception(
            "Failed to retrieve pipeline execution history."
        )

        raise HTTPException(
            status_code=500,
            detail="Unable to retrieve pipeline execution history.",
        )


@router.get("/runs/{run_id}")
def get_pipeline_run(
    run_id: int,
    db: Session = Depends(get_db),
):
    """
    Retrieve an individual ELT pipeline execution.
    """

    run = get_pipeline_run_by_id(
        db=db,
        run_id=run_id,
    )

    if run is None:
        raise HTTPException(
            status_code=404,
            detail="Pipeline execution not found.",
        )

    return {
        "status": "success",
        "run": {
            "id": run.id,
            "batch_id": run.batch_id,
            "status": run.status,
            "extracted_records": run.extracted_records,
            "previously_processed": run.previously_processed,
            "batch_duplicates": run.batch_duplicates,
            "new_records": run.new_records,
            "loaded_records": run.loaded_records,
            "recovered_batch": run.recovered_batch,
            "started_at": run.started_at,
            "completed_at": run.completed_at,
            "duration_seconds": run.duration_seconds,
            "error_message": run.error_message,
        },
    }
