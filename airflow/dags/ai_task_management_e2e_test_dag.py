
import logging
import os
from datetime import timedelta
from pathlib import Path

import pendulum

from airflow.sdk import DAG
from airflow.providers.standard.operators.python import PythonOperator


logger = logging.getLogger(__name__)

PROJECT_DIR = Path("/opt/airflow/project")

TEST_DATABASE = "AI_TASK_MANAGEMENT_TEST_DB"
TEST_RAW_SCHEMA = "AIRFLOW_TEST_RAW"
TEST_STAGING_SCHEMA = "AIRFLOW_TEST_STAGING"
TEST_ANALYTICS_SCHEMA = "AIRFLOW_TEST_ANALYTICS"

TEST_BATCH_ID = "11111111-1111-4111-8111-111111111111"

TEST_TASK = {
    "userId": 900001,
    "id": 900001,
    "title": "Airflow isolated ELT integration test",
    "completed": True,
}


def prepare_test_environment():
    """Validate the project and isolated Snowflake configuration."""

    if not PROJECT_DIR.is_dir():
        raise FileNotFoundError(
            f"Project directory not found: {PROJECT_DIR}"
        )

    os.chdir(PROJECT_DIR)

    expected_variables = {
        "SNOWFLAKE_DATABASE": TEST_DATABASE,
        "SNOWFLAKE_RAW_SCHEMA": TEST_RAW_SCHEMA,
        "SNOWFLAKE_STAGING_SCHEMA": TEST_STAGING_SCHEMA,
        "SNOWFLAKE_ANALYTICS_SCHEMA": TEST_ANALYTICS_SCHEMA,
    }

    for variable, expected_value in expected_variables.items():

        actual_value = os.getenv(variable)

        if actual_value != expected_value:
            raise RuntimeError(
                f"Unsafe test configuration for {variable}. "
                f"Expected {expected_value}, got {actual_value}."
            )

    logger.info(
        "Isolated Snowflake test configuration verified."
    )


def load_test_record():
    """Load the synthetic test record into isolated RAW."""

    prepare_test_environment()

    from api_elt_pipeline.load.snowflake_loader import (
        load_tasks_to_snowflake,
    )

    result = load_tasks_to_snowflake(
        tasks=[TEST_TASK],
        batch_id=TEST_BATCH_ID,
        source_extracted_at="2026-11-19T00:00:00+00:00",
    )

    if result != 1:
        raise RuntimeError(
            f"Expected 1 RAW record, received {result}."
        )

    logger.info(
        "Synthetic RAW record loaded successfully."
    )


def transform_staging():
    """Execute the isolated RAW-to-STAGING transformation."""

    prepare_test_environment()

    from api_elt_pipeline.load.sql_runner import run_sql_file

    run_sql_file(
        "snowflake_api_pipeline/03_staging_transform.sql"
    )

    logger.info("STAGING transformation completed.")


def transform_analytics():
    """Execute the isolated STAGING-to-ANALYTICS transformation."""

    prepare_test_environment()

    from api_elt_pipeline.load.sql_runner import run_sql_file

    run_sql_file(
        "snowflake_api_pipeline/04_analytics_transform.sql"
    )

    logger.info("ANALYTICS transformation completed.")


def validate_test_results():
    """Verify the final isolated analytics record."""

    prepare_test_environment()

    from api_elt_pipeline.load.snowflake_connection import (
        get_snowflake_connection,
    )

    connection = None
    cursor = None

    try:
        connection = get_snowflake_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT
                USER_ID,
                TOTAL_TASKS,
                COMPLETED_TASKS,
                PENDING_TASKS,
                COMPLETION_RATE
            FROM
                AI_TASK_MANAGEMENT_TEST_DB
                .AIRFLOW_TEST_ANALYTICS.TASK_SUMMARY
            WHERE USER_ID = %s
            """,
            (900001,),
        )

        result = cursor.fetchone()

        expected_result = (
            900001,
            1,
            1,
            0,
            100.0,
        )

        if result is None:
            raise RuntimeError(
                "Analytics test record was not found."
            )

        if tuple(result) != expected_result:
            raise AssertionError(
                f"Analytics validation failed. "
                f"Expected {expected_result}, got {tuple(result)}"
            )

        logger.info(
            "End-to-end Snowflake validation successful: %s",
            result,
        )

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()


default_args = {
    "owner": "data-engineering",
    "depends_on_past": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}


with DAG(
    dag_id="ai_task_management_e2e_test_dag",
    description=(
        "Tests isolated RAW, STAGING and ANALYTICS "
        "Snowflake transformations."
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
        "integration-test",
    ],
) as dag:

    load_raw = PythonOperator(
        task_id="load_test_record",
        python_callable=load_test_record,
        do_xcom_push=False,
    )

    staging = PythonOperator(
        task_id="transform_staging",
        python_callable=transform_staging,
        do_xcom_push=False,
    )

    analytics = PythonOperator(
        task_id="transform_analytics",
        python_callable=transform_analytics,
        do_xcom_push=False,
    )

    validate = PythonOperator(
        task_id="validate_test_results",
        python_callable=validate_test_results,
        do_xcom_push=False,
    )

    load_raw >> staging >> analytics >> validate
