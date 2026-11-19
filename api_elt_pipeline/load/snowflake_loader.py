
import logging
import os
import re

from datetime import datetime, timezone

from api_elt_pipeline.load.snowflake_connection import (
    get_snowflake_connection,
)

logger = logging.getLogger(__name__)

IDENTIFIER_PATTERN = r"[A-Za-z_][A-Za-z0-9_$]*"


def load_tasks_to_snowflake(
    tasks,
    batch_id,
    source_extracted_at,
):
    """
    Load a batch into Snowflake RAW using batch-aware MERGE.

    Configurable environment variables:

        SNOWFLAKE_DATABASE
        SNOWFLAKE_RAW_SCHEMA

    Default RAW schema:
        RAW

    Isolated test RAW schema:
        AIRFLOW_TEST_RAW

    Repeated sequential loads of the same batch do not
    insert duplicate TASK_ID records within that batch.
    """

    if not tasks:
        logger.info("No tasks available to load.")
        return 0

    if not batch_id:
        raise ValueError("Batch ID is required.")

    if not source_extracted_at:
        raise ValueError(
            "Source extraction timestamp is required."
        )

    # --------------------------------------------------
    # 1. Read and validate database configuration
    # --------------------------------------------------

    database = os.getenv("SNOWFLAKE_DATABASE")

    if not database:
        raise ValueError(
            "SNOWFLAKE_DATABASE is not configured."
        )

    if not re.fullmatch(
        IDENTIFIER_PATTERN,
        database,
    ):
        raise ValueError(
            "Invalid Snowflake database name."
        )

    # --------------------------------------------------
    # 2. Read and validate RAW schema configuration
    # --------------------------------------------------

    raw_schema = os.getenv(
        "SNOWFLAKE_RAW_SCHEMA",
        "RAW",
    )

    if not re.fullmatch(
        IDENTIFIER_PATTERN,
        raw_schema,
    ):
        raise ValueError(
            "Invalid Snowflake RAW schema name."
        )

    target_table = (
        f"{database}.{raw_schema}.TASKS_RAW"
    )

    temporary_table = (
        f"{database}.{raw_schema}.TMP_TASKS_RAW"
    )

    logger.info(
        "Snowflake RAW target: %s",
        target_table,
    )

    # --------------------------------------------------
    # 3. Normalize timestamps
    # --------------------------------------------------

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

        # --------------------------------------------------
        # 4. Establish Snowflake connection
        # --------------------------------------------------

        connection = get_snowflake_connection()
        cursor = connection.cursor()

        # --------------------------------------------------
        # 5. Create isolated temporary RAW table
        # --------------------------------------------------

        cursor.execute(
            f"""
            CREATE TEMPORARY TABLE {temporary_table}
            LIKE {target_table}
            """
        )

        # --------------------------------------------------
        # 6. Insert extracted records into temporary table
        # --------------------------------------------------

        insert_query = f"""
            INSERT INTO {temporary_table} (
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

        cursor.executemany(
            insert_query,
            records,
        )

        logger.info(
            "Inserted %s records into temporary RAW table.",
            len(records),
        )

        # --------------------------------------------------
        # 7. Merge into configured RAW target table
        # --------------------------------------------------

        merge_query = f"""
            MERGE INTO {target_table} AS target

            USING {temporary_table} AS source

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

        # --------------------------------------------------
        # 8. Verify records loaded for this batch
        # --------------------------------------------------

        cursor.execute(
            f"""
            SELECT COUNT(*)
            FROM {target_table}
            WHERE BATCH_ID = %s
            """,
            (batch_id,),
        )

        result = cursor.fetchone()
        batch_record_count = result[0]

        # --------------------------------------------------
        # 9. Commit transaction
        # --------------------------------------------------

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

            logger.info(
                "Snowflake connection closed."
            )
