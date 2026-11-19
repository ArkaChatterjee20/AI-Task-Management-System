
import logging
import os
from datetime import timedelta
from pathlib import Path

import pendulum

from airflow.sdk import DAG
from airflow.providers.standard.operators.python import PythonOperator


logger = logging.getLogger(__name__)


def run_existing_elt_pipeline():
    """
    Execute the existing ELT pipeline from the project root.

    Preserve the existing extraction, validation, deduplication,
    recovery and Snowflake loading logic.
    """

    project_dir = Path("/opt/airflow/project")

    if not project_dir.is_dir():
        raise FileNotFoundError(
            f"Project directory not found: {project_dir}"
        )

    # Ensure relative paths resolve from the project root.
    os.chdir(project_dir)

    logger.info("Working directory: %s", Path.cwd())

    # Verify required project paths.
    required_paths = [
        project_dir / "api_elt_pipeline" / "main.py",
        project_dir / "snowflake_api_pipeline",
    ]

    for path in required_paths:
        if not path.exists():
            raise FileNotFoundError(
                f"Required ELT path not found: {path}"
            )

    # Use dedicated persistent storage for RAW files and checkpoints.
    data_dir = Path(
        os.getenv(
            "ELT_DATA_DIR",
            str(project_dir / "data")
        )
    )

    data_dir.mkdir(parents=True, exist_ok=True)

    if not data_dir.is_dir():
        raise NotADirectoryError(
            f"ELT storage path is not a directory: {data_dir}"
        )

    logger.info("ELT data directory: %s", data_dir)

    # Import the existing pipeline only when the task executes.
    from api_elt_pipeline.main import main

    logger.info("Starting AI Task Management ELT pipeline.")

    result = main()

    if not isinstance(result, dict):
        raise TypeError(
            "ELT pipeline must return a dictionary."
        )

    status = result.get("status")

    if status not in {"SUCCESS", "NO_NEW_RECORDS"}:
        raise RuntimeError(
            f"Unexpected ELT pipeline status: {status}"
        )

    logger.info(
        "ELT pipeline completed. Result: %s",
        result
    )

    return result


default_args = {
    "owner": "data-engineering",
    "depends_on_past": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}


with DAG(
    dag_id="ai_task_management_elt_dag",
    description=(
        "Orchestrates the existing AI Task Management ELT pipeline."
    ),
    default_args=default_args,
    start_date=pendulum.datetime(2026, 1, 1, tz="UTC"),
    schedule=None,
    catchup=False,
    max_active_runs=1,
    max_active_tasks=1,
    tags=[
        "ai-task-management",
        "elt",
        "snowflake",
    ],
) as dag:

    run_elt_pipeline = PythonOperator(
        task_id="run_existing_elt_pipeline",
        python_callable=run_existing_elt_pipeline,
        do_xcom_push=False,
    )
