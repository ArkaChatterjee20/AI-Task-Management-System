
from api_elt_pipeline.load.snowflake_connection import (
    get_snowflake_connection,
)


def iter_task_features(batch_size=1000):
    """
    Retrieve task features incrementally from Snowflake.

    Yields one batch at a time to reduce memory usage.
    """

    if not isinstance(batch_size, int) or isinstance(batch_size, bool) or batch_size <= 0:
        raise ValueError("batch_size must be a positive integer.")

    connection = get_snowflake_connection()
    cursor = None

    try:
        cursor = connection.cursor()

        query = """
            SELECT
                TASK_ID,
                TASK_TITLE
            FROM AI_TASK_MANAGEMENT_DB.FEATURES.TASK_TEXT_FEATURES
            ORDER BY TASK_ID
        """

        cursor.execute(query)

        while True:
            rows = cursor.fetchmany(batch_size)

            if not rows:
                break

            yield [
                {
                    "task_id": row[0],
                    "task_title": row[1],
                }
                for row in rows
            ]

    finally:
        if cursor is not None:
            cursor.close()

        connection.close()


def load_task_features():
    """
    Preserve the existing interface by returning all features as a list.
    """

    return [
        feature
        for batch in iter_task_features(batch_size=1000)
        for feature in batch
    ]
