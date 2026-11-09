from datetime import datetime, timezone
from uuid import uuid4

from api_elt_pipeline.load.snowflake_loader import load_tasks_to_snowflake
from api_elt_pipeline.load.snowflake_connection import get_snowflake_connection

batch_id = str(uuid4())
task_id = 987654322

tasks = [{
    "userId": 1,
    "id": task_id,
    "title": "Idempotency verification",
    "completed": False,
}]

source_extracted_at = datetime.now(timezone.utc).isoformat()

try:
    first_count = load_tasks_to_snowflake(
        tasks, batch_id, source_extracted_at
    )
    print("First load count:", first_count)

    second_count = load_tasks_to_snowflake(
        tasks, batch_id, source_extracted_at
    )
    print("Second load count:", second_count)

    conn = get_snowflake_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT COUNT(*)
        FROM AI_TASK_MANAGEMENT_DB.RAW.TASKS_RAW
        WHERE BATCH_ID = %s AND TASK_ID = %s
        """,
        (batch_id, task_id),
    )

    actual_count = cur.fetchone()[0]
    print("Actual records in Snowflake:", actual_count)

    cur.close()
    conn.close()

    assert first_count == 1
    assert second_count == 1
    assert actual_count == 1

    print("IDEMPOTENCY TEST PASSED")

finally:
    conn = get_snowflake_connection()
    cur = conn.cursor()

    cur.execute(
        """
        DELETE FROM AI_TASK_MANAGEMENT_DB.RAW.TASKS_RAW
        WHERE BATCH_ID = %s AND TASK_ID = %s
        """,
        (batch_id, task_id),
    )

    conn.commit()
    print("Test record cleaned up.")

    cur.close()
    conn.close()
