from api_elt_pipeline.load.snowflake_connection import (
    get_snowflake_connection,
)


def get_task_summary():
    """
    Fetch task summary data from Snowflake.
    """

    connection = get_snowflake_connection()

    try:
        cursor = connection.cursor()

        query = """
            SELECT
                USER_ID,
                TOTAL_TASKS,
                COMPLETED_TASKS,
                PENDING_TASKS,
                COMPLETION_RATE
            FROM AI_TASK_MANAGEMENT_DB.ANALYTICS.TASK_SUMMARY
            ORDER BY USER_ID
        """

        cursor.execute(query)

        rows = cursor.fetchall()

        columns = [
            "user_id",
            "total_tasks",
            "completed_tasks",
            "pending_tasks",
            "completion_rate",
        ]

        results = [
            dict(zip(columns, row))
            for row in rows
        ]

        return results

    finally:
        cursor.close()
        connection.close()
def get_all_tasks():
    """
    Fetch all tasks from the Snowflake STAGING layer.
    """

    connection = get_snowflake_connection()
    cursor = None

    try:
        cursor = connection.cursor()

        query = """
            SELECT
                TASK_ID,
                USER_ID,
                TASK_TITLE,
                COMPLETION_STATUS,
                IS_COMPLETED,
                EXTRACTED_AT
            FROM AI_TASK_MANAGEMENT_DB.STAGING.TASKS_STAGING
            ORDER BY TASK_ID
        """

        cursor.execute(query)
        rows = cursor.fetchall()

        columns = [
            "task_id",
            "user_id",
            "task_title",
            "completion_status",
            "is_completed",
            "extracted_at",
        ]

        return [
            dict(zip(columns, row))
            for row in rows
        ]

    finally:
        if cursor:
            cursor.close()
        connection.close()


def get_task_by_id(task_id: int):
    """
    Fetch one task by its ID.
    """

    connection = get_snowflake_connection()
    cursor = None

    try:
        cursor = connection.cursor()

        query = """
            SELECT
                TASK_ID,
                USER_ID,
                TASK_TITLE,
                COMPLETION_STATUS,
                IS_COMPLETED,
                EXTRACTED_AT
            FROM AI_TASK_MANAGEMENT_DB.STAGING.TASKS_STAGING
            WHERE TASK_ID = %s
        """

        cursor.execute(query, (task_id,))
        row = cursor.fetchone()

        if row is None:
            return None

        columns = [
            "task_id",
            "user_id",
            "task_title",
            "completion_status",
            "is_completed",
            "extracted_at",
        ]

        return dict(zip(columns, row))

    finally:
        if cursor:
            cursor.close()
        connection.close()