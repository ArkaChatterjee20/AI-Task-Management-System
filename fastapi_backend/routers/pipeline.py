
from fastapi import APIRouter, HTTPException
import logging

from api_elt_pipeline.main import main as run_elt_pipeline


router = APIRouter(
    prefix="/pipeline",
    tags=["Pipeline"],
)


@router.post("/run")
def run_pipeline():
    """
    Trigger the ELT pipeline and return execution metrics.
    """

    try:
        logging.info("Pipeline execution requested through FastAPI.")

        # Execute the existing ELT pipeline.
        result = run_elt_pipeline()

        # Handle the case where no new records are available.
        if result["status"] == "NO_NEW_RECORDS":
            return {
                **result,
                "message": "No new records available for processing.",
            }

        logging.info(
            "ELT pipeline completed. Batch ID: %s | Records loaded: %s",
            result["batch_id"],
            result["loaded_records_count"],
        )

        return {
            **result,
            "message": "ELT pipeline completed successfully.",
        }

    except Exception as error:

        logging.exception(
            "Pipeline execution failed: %s",
            error,
        )

        raise HTTPException(
            status_code=500,
            detail="ELT pipeline execution failed.",
        )
