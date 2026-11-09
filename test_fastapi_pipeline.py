
from unittest.mock import patch

from fastapi.testclient import TestClient
from fastapi_backend.main import app


client = TestClient(app)


def test_pipeline_success():

    mock_result = {
        "status": "SUCCESS",
        "batch_id": "test-batch-001",
        "extracted_records_count": 4,
        "previously_processed_count": 1,
        "batch_duplicate_count": 1,
        "new_records_count": 2,
        "loaded_records_count": 2,
        "recovered_batch": False,
    }

    with patch(
        "fastapi_backend.routers.pipeline.run_elt_pipeline",
        return_value=mock_result,
    ):
        response = client.post("/pipeline/run")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "SUCCESS"
    assert data["batch_id"] == "test-batch-001"
    assert data["extracted_records_count"] == 4
    assert data["previously_processed_count"] == 1
    assert data["batch_duplicate_count"] == 1
    assert data["new_records_count"] == 2
    assert data["loaded_records_count"] == 2
    assert data["recovered_batch"] is False

    print("SUCCESS response: PASS")


def test_pipeline_no_new_records():

    mock_result = {
        "status": "NO_NEW_RECORDS",
        "batch_id": None,
        "extracted_records_count": 4,
        "previously_processed_count": 4,
        "batch_duplicate_count": 0,
        "new_records_count": 0,
        "loaded_records_count": 0,
        "recovered_batch": False,
    }

    with patch(
        "fastapi_backend.routers.pipeline.run_elt_pipeline",
        return_value=mock_result,
    ):
        response = client.post("/pipeline/run")

    assert response.status_code == 200

    data = response.json()

    assert data["status"] == "NO_NEW_RECORDS"
    assert data["new_records_count"] == 0
    assert data["loaded_records_count"] == 0

    print("NO_NEW_RECORDS response: PASS")


def test_pipeline_failure():

    with patch(
        "fastapi_backend.routers.pipeline.run_elt_pipeline",
        side_effect=RuntimeError("Simulated pipeline failure"),
    ):
        response = client.post("/pipeline/run")

    assert response.status_code == 500
    assert response.json()["detail"] == (
        "ELT pipeline execution failed."
    )

    print("FAILURE response: PASS")


if __name__ == "__main__":

    test_pipeline_success()
    test_pipeline_no_new_records()
    test_pipeline_failure()

    print("\nALL FASTAPI PIPELINE TESTS PASSED")

