from uuid import uuid4
from pathlib import Path
from unittest.mock import patch

from api_elt_pipeline import main as pipeline_module
from api_elt_pipeline.storage.raw_storage import save_raw_tasks
from api_elt_pipeline.state.pending_batch_manager import (
    save_pending_batch,
    load_pending_batch,
    clear_pending_batch,
)
from api_elt_pipeline.load.snowflake_connection import get_snowflake_connection

task_id = 900000000 + (uuid4().int % 90000000)
task_id = int(task_id)

task = {
    "userId": 1,
    "id": task_id,
    "title": "Temporary recovery integration test",
    "completed": False,
}

raw_file = None
batch_id = None
test_passed = False

try:
    # Confirm the synthetic task ID is not already present.
    conn = get_snowflake_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT COUNT(*)
        FROM AI_TASK_MANAGEMENT_DB.RAW.TASKS_RAW
        WHERE TASK_ID = %s
        """,
        (task_id,),
    )

    if cur.fetchone()[0] != 0:
        raise RuntimeError("Generated test task ID already exists.")

    cur.close()
    conn.close()

    # Create and register a real RAW batch.
    raw_file = save_raw_tasks([task])
    save_pending_batch(raw_file)

    from api_elt_pipeline.storage.raw_storage import load_raw_tasks
    payload = load_raw_tasks(raw_file)
    batch_id = payload["batch_id"]

    print("Test batch created:", batch_id)

    # First attempt: real Snowflake load, simulated SQL failure.
    with patch.object(
        pipeline_module,
        "run_sql_file",
        side_effect=RuntimeError("Simulated transformation failure"),
    ), patch.object(
        pipeline_module,
        "save_processed_ids",
    ), patch.object(
        pipeline_module,
        "load_processed_ids",
        return_value=set(),
    ), patch.object(
        pipeline_module,
        "extract_tasks",
    ) as extract_mock:

        try:
            pipeline_module.main()
        except RuntimeError as error:
            print("Expected first-run failure:", error)

        extract_mock.assert_not_called()

    if load_pending_batch() is None:
        raise AssertionError("Pending batch was lost after failure.")

    print("Pending batch retained after failure: PASS")

    # Second attempt: recover the same batch and load it again.
    with patch.object(
        pipeline_module,
        "run_sql_file",
    ) as sql_mock, patch.object(
        pipeline_module,
        "save_processed_ids",
    ) as checkpoint_mock, patch.object(
        pipeline_module,
        "load_processed_ids",
        return_value=set(),
    ), patch.object(
        pipeline_module,
        "extract_tasks",
    ) as extract_mock:

        pipeline_module.main()

        extract_mock.assert_not_called()
        assert sql_mock.call_count == 2
        checkpoint_mock.assert_called_once()

    if load_pending_batch() is not None:
        raise AssertionError("Pending batch was not cleared.")

    print("Pending batch recovered: PASS")
    print("API extraction skipped during recovery: PASS")

    # Verify the real Snowflake RAW table.
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

    cur.close()
    conn.close()

    print("Snowflake records for test batch:", actual_count)

    assert actual_count == 1

    print("REAL SNOWFLAKE RECOVERY TEST PASSED")
    test_passed = True

finally:
    # Remove only this test's Snowflake record.
    if batch_id is not None:
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
        cur.close()
        conn.close()

    clear_pending_batch()

    if raw_file is not None and Path(raw_file).exists():
        Path(raw_file).unlink()

    print("Temporary test data cleaned up.")
