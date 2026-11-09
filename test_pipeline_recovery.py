from pathlib import Path
from importlib import import_module
from unittest.mock import patch

pipeline = import_module("api_elt_pipeline.main")

raw_file = Path(
    "data/raw/todos_20261104_123151_d537f096-6685-4bce-a271-6fad8c23848a.json"
).resolve()

assert raw_file.exists(), "Test RAW JSON file does not exist."

payload = pipeline.load_raw_tasks(raw_file)

processed_ids = set(range(1, 201))
expected_ids = {task["id"] for task in payload["data"]}

with patch.object(pipeline, "load_pending_batch", return_value=raw_file), \
     patch.object(pipeline, "extract_tasks") as extract_mock, \
     patch.object(pipeline, "save_pending_batch") as save_pending_mock, \
     patch.object(pipeline, "load_tasks_to_snowflake",
                  return_value=len(payload["data"])) as loader_mock, \
     patch.object(pipeline, "run_sql_file") as sql_mock, \
     patch.object(pipeline, "load_processed_ids",
                  return_value=processed_ids), \
     patch.object(pipeline, "save_processed_ids") as checkpoint_mock, \
     patch.object(pipeline, "clear_pending_batch") as clear_mock:

    pipeline.main()

    extract_mock.assert_not_called()
    save_pending_mock.assert_not_called()

    loader_mock.assert_called_once_with(
        tasks=payload["data"],
        batch_id=payload["batch_id"],
        source_extracted_at=payload["extracted_at"],
    )

    assert sql_mock.call_count == 2
    checkpoint_mock.assert_called_once()
    clear_mock.assert_called_once()

    saved_ids = checkpoint_mock.call_args.args[0]
    assert saved_ids == processed_ids.union(expected_ids)

    print("API extraction skipped: PASS")
    print("Pending RAW batch recovered: PASS")
    print("Snowflake loader invoked: PASS")
    print("Both SQL transformations invoked: PASS")
    print("Checkpoint update requested: PASS")
    print("Pending state cleared: PASS")
    print("RECOVERY ORCHESTRATION TEST PASSED")
