
from importlib import import_module
from unittest.mock import patch

pipeline = import_module("api_elt_pipeline.main")

# Four extracted records:
# ID 101: New
# ID 102: New
# ID 101: Duplicate within this batch
# ID 103: Already processed

tasks = [
    {"userId": 1, "id": 101, "title": "Task A", "completed": False},
    {"userId": 1, "id": 102, "title": "Task B", "completed": True},
    {"userId": 1, "id": 101, "title": "Task A duplicate", "completed": False},
    {"userId": 2, "id": 103, "title": "Task C", "completed": True},
]

raw_payload = {
    "batch_id": "test-normal-batch-001",
    "extracted_at": "2026-11-06T10:00:00Z",
    "record_count": 2,
    "data": tasks[:2],
}

with patch.object(
    pipeline, "load_pending_batch", return_value=None
), patch.object(
    pipeline, "extract_tasks", return_value=tasks
) as extract_mock, patch.object(
    pipeline, "load_processed_ids",
    side_effect=[{103}, {103}]
), patch.object(
    pipeline, "save_raw_tasks", return_value="fake_raw.json"
) as raw_save_mock, patch.object(
    pipeline, "save_pending_batch"
) as pending_save_mock, patch.object(
    pipeline, "load_raw_tasks", return_value=raw_payload
), patch.object(
    pipeline, "load_tasks_to_snowflake", return_value=2
) as loader_mock, patch.object(
    pipeline, "run_sql_file"
) as sql_mock, patch.object(
    pipeline, "save_processed_ids"
) as checkpoint_mock, patch.object(
    pipeline, "clear_pending_batch"
) as clear_mock:

    result = pipeline.main()

    # Verify extraction.
    extract_mock.assert_called_once()

    # Verify only new records were saved.
    raw_save_mock.assert_called_once_with(tasks[:2])

    # Verify pending batch registration.
    pending_save_mock.assert_called_once()

    # Verify Snowflake loading.
    loader_mock.assert_called_once()

    # Verify both SQL transformations.
    assert sql_mock.call_count == 2

    # Verify checkpoint and pending state.
    checkpoint_mock.assert_called_once()
    clear_mock.assert_called_once()

    saved_ids = checkpoint_mock.call_args.args[0]
    assert saved_ids == {101, 102, 103}

    # Verify returned execution metrics.
    assert result["status"] == "SUCCESS"
    assert result["batch_id"] == "test-normal-batch-001"
    assert result["extracted_records_count"] == 4
    assert result["previously_processed_count"] == 1
    assert result["batch_duplicate_count"] == 1
    assert result["new_records_count"] == 2
    assert result["loaded_records_count"] == 2
    assert result["recovered_batch"] is False

    print("API extraction: PASS")
    print("Deduplication statistics: PASS")
    print("RAW batch saving: PASS")
    print("Snowflake loading: PASS")
    print("SQL transformations: PASS")
    print("Checkpoint update: PASS")
    print("Execution metrics: PASS")
    print("NORMAL EXTRACTION METRICS TEST PASSED")
