from api_elt_pipeline.load.snowflake_connection import (
    get_snowflake_connection,
)


def get_prediction_runs(limit=20):
    """Retrieve recent prediction runs."""

    connection = get_snowflake_connection()
    cursor = connection.cursor()

    try:
        query = """
        SELECT
            RUN_ID,
            TOTAL_PREDICTIONS,
            RUN_STATUS,
            STARTED_AT,
            COMPLETED_AT
        FROM PREDICTION_RUNS
        ORDER BY STARTED_AT DESC
        LIMIT %s
        """

        cursor.execute(query, (limit,))

        columns = [col[0] for col in cursor.description]

        return [
            dict(zip(columns, row))
            for row in cursor.fetchall()
        ]

    finally:
        cursor.close()
        connection.close()


def get_prediction_run(run_id):
    """Retrieve one prediction run."""

    connection = get_snowflake_connection()
    cursor = connection.cursor()

    try:
        query = """
        SELECT
            RUN_ID,
            TOTAL_PREDICTIONS,
            RUN_STATUS,
            STARTED_AT,
            COMPLETED_AT
        FROM PREDICTION_RUNS
        WHERE RUN_ID = %s
        """

        cursor.execute(query, (run_id,))

        row = cursor.fetchone()

        if row is None:
            return None

        columns = [col[0] for col in cursor.description]

        return dict(zip(columns, row))

    finally:
        cursor.close()
        connection.close()


def get_prediction_history(run_id, limit=100):
    """Retrieve prediction history for a specific run."""

    connection = get_snowflake_connection()
    cursor = connection.cursor()

    try:
        query = """
        SELECT
            RUN_ID,
            TASK_ID,
            TASK_TITLE,
            PREDICTION,
            PREDICTED_STATUS,
            PREDICTED_AT
        FROM TASK_PREDICTION_HISTORY
        WHERE RUN_ID = %s
        ORDER BY PREDICTED_AT DESC
        LIMIT %s
        """

        cursor.execute(query, (run_id, limit))

        columns = [col[0] for col in cursor.description]

        return [
            dict(zip(columns, row))
            for row in cursor.fetchall()
        ]

    finally:
        cursor.close()
        connection.close()


def get_recent_predictions(limit=100):
    """Retrieve recent predictions across all runs."""

    connection = get_snowflake_connection()
    cursor = connection.cursor()

    try:
        query = """
        SELECT
            RUN_ID,
            TASK_ID,
            TASK_TITLE,
            PREDICTION,
            PREDICTED_STATUS,
            PREDICTED_AT
        FROM TASK_PREDICTION_HISTORY
        ORDER BY PREDICTED_AT DESC
        LIMIT %s
        """

        cursor.execute(query, (limit,))

        columns = [col[0] for col in cursor.description]

        return [
            dict(zip(columns, row))
            for row in cursor.fetchall()
        ]

    finally:
        cursor.close()
        connection.close()

def get_prediction_history_paginated(
    run_id,
    page=1,
    page_size=100,
):
    """
    Retrieve prediction history using pagination.
    """

    if not isinstance(page, int) or isinstance(page, bool) or page < 1:
        raise ValueError("Page must be a positive integer.")

    if (
        not isinstance(page_size, int)
        or isinstance(page_size, bool)
        or not 1 <= page_size <= 1000
    ):
        raise ValueError("Page size must be between 1 and 1000.")

    offset = (page - 1) * page_size

    connection = get_snowflake_connection()
    cursor = connection.cursor()

    try:
        # Get total number of records.
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM TASK_PREDICTION_HISTORY
            WHERE RUN_ID = %s
            """,
            (run_id,),
        )

        total_records = cursor.fetchone()[0]

        # Retrieve only the requested page.
        cursor.execute(
            """
            SELECT
                RUN_ID,
                TASK_ID,
                TASK_TITLE,
                PREDICTION,
                PREDICTED_STATUS,
                PREDICTED_AT
            FROM TASK_PREDICTION_HISTORY
            WHERE RUN_ID = %s
            ORDER BY PREDICTED_AT DESC, TASK_ID DESC
            LIMIT %s OFFSET %s
            """,
            (run_id, page_size, offset),
        )

        columns = [col[0] for col in cursor.description]

        predictions = [
            dict(zip(columns, row))
            for row in cursor.fetchall()
        ]

        return {
            "total_records": total_records,
            "page": page,
            "page_size": page_size,
            "total_pages": (
                (total_records + page_size - 1) // page_size
            ),
            "predictions": predictions,
        }

    finally:
        cursor.close()
        connection.close()

