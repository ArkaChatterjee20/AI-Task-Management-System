import uuid

from api_elt_pipeline.load.snowflake_connection import (
    get_snowflake_connection,
)


def start_pipeline_run(pipeline_name):
    """Create a pipeline run and return its exact generated RUN_ID."""

    if not isinstance(pipeline_name, str) or not pipeline_name.strip():
        raise ValueError("pipeline_name must be a non-empty string")

    if len(pipeline_name) > 100:
        raise ValueError("pipeline_name cannot exceed 100 characters")

    connection = get_snowflake_connection()
    cursor = connection.cursor()

    temporary_name = uuid.uuid4().hex

    try:
        connection.autocommit(False)

        insert_query = """
        INSERT INTO PIPELINE_RUNS (
            PIPELINE_NAME,
            STATUS,
            START_TIME
        )
        VALUES (
            %s,
            'RUNNING',
            CURRENT_TIMESTAMP()
        )
        """

        cursor.execute(insert_query, (temporary_name,))

        cursor.execute(
            """
            SELECT RUN_ID
            FROM PIPELINE_RUNS
            WHERE PIPELINE_NAME = %s
            """,
            (temporary_name,),
        )

        result = cursor.fetchone()

        if result is None:
            raise RuntimeError(
                "Could not retrieve the generated pipeline RUN_ID"
            )

        run_id = result[0]

        cursor.execute(
            """
            UPDATE PIPELINE_RUNS
            SET PIPELINE_NAME = %s
            WHERE RUN_ID = %s
            """,
            (pipeline_name, run_id),
        )

        if cursor.rowcount != 1:
            raise RuntimeError(
                "Could not restore the original pipeline name"
            )

        connection.commit()

        return run_id

    except Exception:
        connection.rollback()
        raise

    finally:
        cursor.close()
        connection.close()


def complete_pipeline_run(run_id, records_processed):
    """Mark a pipeline run as successful."""

    connection = get_snowflake_connection()
    cursor = connection.cursor()

    try:
        query = """
        UPDATE PIPELINE_RUNS
        SET
            STATUS = 'SUCCESS',
            END_TIME = CURRENT_TIMESTAMP(),
            RECORDS_PROCESSED = %s
        WHERE RUN_ID = %s
        """

        cursor.execute(query, (records_processed, run_id))
        connection.commit()

    finally:
        cursor.close()
        connection.close()


def fail_pipeline_run(run_id, error_message):
    """Mark a pipeline run as failed."""

    connection = get_snowflake_connection()
    cursor = connection.cursor()

    try:
        query = """
        UPDATE PIPELINE_RUNS
        SET
            STATUS = 'FAILED',
            END_TIME = CURRENT_TIMESTAMP(),
            ERROR_MESSAGE = %s
        WHERE RUN_ID = %s
        """

        cursor.execute(query, (error_message, run_id))
        connection.commit()

    finally:
        cursor.close()
        connection.close()
