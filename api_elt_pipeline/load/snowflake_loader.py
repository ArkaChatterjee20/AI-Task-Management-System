
import logging

from datetime import datetime, timezone

from api_elt_pipeline.load.snowflake_connection import (
    get_snowflake_connection,
)

logger = logging.getLogger(__name__)


def load_tasks_to_snowflake(
    tasks,
    batch_id,
    source_extracted_at,
):
    """
    Load a batch into Snowflake RAW using batch-aware MERGE.

    Repeated sequential loads of the same batch do not
    insert duplicate TASK_ID records within that batch.
    """

    if not tasks:
        logger.info("No tasks available to load.")
        return 0

    if not batch_id:
        raise ValueError("Batch ID is required.")

    if not source_extracted_at:
        raise ValueError("Source extraction timestamp is required.")

    # Convert the source timestamp to UTC without timezone
    # information because the Snowflake column is TIMESTAMP_NTZ.
    source_timestamp = datetime.fromisoformat(
        source_extracted_at
    )

    if source_timestamp.tzinfo is not None:
        source_timestamp = source_timestamp.astimezone(
            timezone.utc
        ).replace(tzinfo=None)

    loaded_at = datetime.now(timezone.utc).replace(
        tzinfo=None
    )

    connection = None
    cursor = None

    try:
        connection = get_snowflake_connection()
        cursor = connection.cursor()

        # Create a session-specific temporary staging table.
        cursor.execute("""
            CREATE TEMPORARY TABLE TMP_TASKS_RAW
            LIKE AI_TASK_MANAGEMENT_DB.RAW.TASKS_RAW
        """)

        insert_query = """
            INSERT INTO TMP_TASKS_RAW (
                USER_ID,
                TASK_ID,
                TITLE,
                COMPLETED,
                EXTRACTED_AT,
                BATCH_ID,
                SOURCE_EXTRACTED_AT
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """

        records = [
            (
                task["userId"],
                task["id"],
                task["title"],
                task["completed"],
                loaded_at,
                batch_id,
                source_timestamp,
            )
            for task in tasks
        ]

        cursor.executemany(insert_query, records)

        merge_query = """
            MERGE INTO AI_TASK_MANAGEMENT_DB.RAW.TASKS_RAW
                AS target
            USING TMP_TASKS_RAW AS source

            ON target.BATCH_ID = source.BATCH_ID
            AND target.TASK_ID = source.TASK_ID

            WHEN NOT MATCHED THEN
                INSERT (
                    USER_ID,
                    TASK_ID,
                    TITLE,
                    COMPLETED,
                    EXTRACTED_AT,
                    BATCH_ID,
                    SOURCE_EXTRACTED_AT
                )
                VALUES (
                    source.USER_ID,
                    source.TASK_ID,
                    source.TITLE,
                    source.COMPLETED,
                    source.EXTRACTED_AT,
                    source.BATCH_ID,
                    source.SOURCE_EXTRACTED_AT
                )
        """

        cursor.execute(merge_query)

        # Count records belonging to this batch.
        cursor.execute(
            """
            SELECT COUNT(*)
            FROM AI_TASK_MANAGEMENT_DB.RAW.TASKS_RAW
            WHERE BATCH_ID = %s
            """,
            (batch_id,),
        )

        result = cursor.fetchone()
        batch_record_count = result[0]

        connection.commit()

        logger.info(
            "Batch %s loaded successfully. Records: %s",
            batch_id,
            batch_record_count,
        )

        return batch_record_count

    except Exception:
        if connection:
            connection.rollback()

        logger.exception(
            "Failed to load batch %s into Snowflake.",
            batch_id,
        )
        raise

    finally:
        if cursor:
            cursor.close()

        if connection:
            connection.close()
