
import time

from sqlalchemy.orm import Session

from fastapi_backend.db_models import ELTPipelineRun


def create_pipeline_run(db: Session) -> ELTPipelineRun:
    """Create a RUNNING pipeline execution record."""

    run = ELTPipelineRun(
        status="RUNNING",
        started_at=None,
    )

    db.add(run)
    db.commit()
    db.refresh(run)

    return run


def complete_pipeline_run(
    db: Session,
    run: ELTPipelineRun,
    result: dict,
) -> ELTPipelineRun:
    """Update execution record after pipeline completion."""

    run.batch_id = result.get("batch_id")
    run.status = result.get("status", "SUCCESS")

    run.extracted_records = result.get(
        "extracted_records_count"
    )

    run.previously_processed = result.get(
        "previously_processed_count"
    )

    run.batch_duplicates = result.get(
        "batch_duplicate_count"
    )

    run.new_records = result.get("new_records_count")
    run.loaded_records = result.get("loaded_records_count")

    run.recovered_batch = result.get(
        "recovered_batch",
        False,
    )

    run.completed_at = __import__("datetime").datetime.now(
        __import__("datetime").timezone.utc
    )

    if run.started_at:
        run.duration_seconds = (
            run.completed_at - run.started_at
        ).total_seconds()

    db.commit()
    db.refresh(run)

    return run


def fail_pipeline_run(
    db: Session,
    run: ELTPipelineRun,
    error_message: str,
) -> ELTPipelineRun:
    """Record a failed pipeline execution."""

    from datetime import datetime, timezone

    run.status = "FAILED"
    run.error_message = error_message
    run.completed_at = datetime.now(timezone.utc)

    if run.started_at:
        run.duration_seconds = (
            run.completed_at - run.started_at
        ).total_seconds()

    db.commit()
    db.refresh(run)

    return run

def get_pipeline_runs(
    db: Session,
    limit: int = 20,
    offset: int = 0,
):
    """Retrieve paginated pipeline execution history."""

    query = db.query(ELTPipelineRun)

    total = query.count()

    runs = (
        query
        .order_by(
            ELTPipelineRun.started_at.desc(),
            ELTPipelineRun.id.desc(),
        )
        .offset(offset)
        .limit(limit)
        .all()
    )

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "runs": [
            {
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
            }
            for run in runs
        ],
    }


def get_pipeline_run_by_id(
    db: Session,
    run_id: int,
):
    """Retrieve an individual pipeline execution."""

    return (
        db.query(ELTPipelineRun)
        .filter(ELTPipelineRun.id == run_id)
        .first()
    )
