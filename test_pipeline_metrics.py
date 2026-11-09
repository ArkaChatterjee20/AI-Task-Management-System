
from pathlib import Path
from importlib import import_module
from unittest.mock import patch

pipeline = import_module("api_elt_pipeline.main")

raw_file = Path(
    "data/raw/todos_20261104_123151_d537f096-6685-4bce-a271-6fad8c23848a.json"
).resolve()

assert raw_file.exists(), "Test RAW JSON file does not exist."

payload = pipeline.load_raw_tasks(raw_file)
expected_count = len(payload["data"])

with patch.object(
    pipeline, "load_pending_batch", return_value=raw_file
), patch.object(
    pipeline, "extract_tasks"
) as extract_mock, patch.object(
    pipeline, "load_tasks_to_snowflake", return_value=expected_count
), patch.object(
    pipeline, "run_sql_file"
), patch.object(
    pipeline, "load_processed_ids", return_value=set()
), patch.object(
    pipeline, "save_processed_ids"
), patch.object(
    pipeline, "clear_pending_batch"
):

    result = pipeline.main()

    assert result["status"] == "SUCCESS"
    assert result["batch_id"] == payload["batch_id"]

    assert result["extracted_records_count"] is None
    assert result["previously_processed_count"] is None
    assert result["batch_duplicate_count"] is None

    assert result["new_records_count"] == expected_count
    assert result["loaded_records_count"] == expected_count
    assert result["recovered_batch"] is True

    extract_mock.assert_not_called()

    print("Pipeline status: PASS")
    print("Batch ID: PASS")
    print("Recovery metrics: PASS")
    print("New records count: PASS")
    print("Loaded records count: PASS")
    print("Recovery flag: PASS")
    print("PIPELINE METRICS TEST PASSED")
