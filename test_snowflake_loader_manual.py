from datetime import datetime, timezone
from uuid import uuid4

from api_elt_pipeline.load.snowflake_loader import load_tasks_to_snowflake
from api_elt_pipeline.load.snowflake_connection import get_snowflake_connection

batch_id = str(uuid4())
test_task_id = 987654321

test_tasks = [
    {
        "userId": 1,
        "id": test_task_id,
        "title": "Temporary Snowflake loader verification",
        "completed": False,
    }
]

source_extracted_at = datetime.now(timezone.utc).isoformat()

try:
    loaded_count = load_tasks_to_snowflake(
        tasks=test_tasks,
        batch_id=batch_id,
        source_extracted_at=source_extracted_at,
    )

    print("Loader returned:", loaded_count)

    if loaded_count != 1:
        raise AssertionError("Expected exactly one loaded record.")

    connection = get_snowflake_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM AI_TASK_MANAGEMENT_DB.RAW.TASKS_RAW
        WHERE BATCH_ID = %s
          AND TASK_ID = %s
        """,
        (batch_id, test_task_id),
    )

    verified_count = cursor.fetchone()[0]

    print("Verified records:", verified_count)

    if verified_count != 1:
        raise AssertionError("Snowflake verification failed.")

    cursor.close()
    connection.close()

    print("SNOWFLAKE LOADER TEST PASSED")

finally:
    connection = get_snowflake_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        DELETE FROM AI_TASK_MANAGEMENT_DB.RAW.TASKS_RAW
        WHERE BATCH_ID = %s
          AND TASK_ID = %s
        """,
        (batch_id, test_task_id),
    )

    connection.commit()
    print("Temporary test record cleaned up.")

    cursor.close()
    connection.close()
