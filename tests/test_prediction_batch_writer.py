from unittest.mock import MagicMock, patch

from fastapi_backend.services.prediction_loader import (
    save_predictions_in_batches,
)


def make_prediction(task_id):
    return {
        "task_id": task_id,
        "task_title": f"Task {task_id}",
        "prediction": 1,
        "predicted_status": "Done",
    }


@patch(
    "fastapi_backend.services.prediction_loader.get_snowflake_connection"
)
def test_batch_writer_saves_multiple_batches(mock_connection):
    connection = MagicMock()
    cursor = MagicMock()

    mock_connection.return_value = connection
    connection.cursor.return_value = cursor

    batches = [
        [make_prediction(101), make_prediction(102)],
        [make_prediction(103), make_prediction(104)],
    ]

    run_id = save_predictions_in_batches(
        iter(batches),
        batch_size=2,
    )

    assert isinstance(run_id, str)
    assert len(run_id) == 36

    assert cursor.executemany.call_count == 4

    connection.commit.assert_called_once()
    cursor.close.assert_called_once()
    connection.close.assert_called_once()
import pytest


@patch(
    "fastapi_backend.services.prediction_loader.get_snowflake_connection"
)
def test_batch_writer_rejects_duplicate_ids(mock_connection):
    batches = [
        [make_prediction(101), make_prediction(102)],
        [make_prediction(102), make_prediction(103)],
    ]

    with pytest.raises(
        ValueError,
        match="Duplicate task_id across batches: 102",
    ):
        save_predictions_in_batches(
            iter(batches),
            batch_size=2,
        )

    mock_connection.assert_not_called()
@patch(
    "fastapi_backend.services.prediction_loader.get_snowflake_connection"
)
def test_batch_writer_rolls_back_on_failure(mock_connection):
    connection = MagicMock()
    cursor = MagicMock()

    mock_connection.return_value = connection
    connection.cursor.return_value = cursor

    cursor.executemany.side_effect = [
        None,
        None,
        RuntimeError("Simulated batch failure"),
    ]

    batches = [
        [make_prediction(101), make_prediction(102)],
        [make_prediction(103), make_prediction(104)],
    ]

    with pytest.raises(
        RuntimeError,
        match="Simulated batch failure",
    ):
        save_predictions_in_batches(
            iter(batches),
            batch_size=2,
        )

    connection.rollback.assert_called_once()
    connection.close.assert_called_once()
    cursor.close.assert_called_once()
@patch(
    "fastapi_backend.services.prediction_loader.get_snowflake_connection"
)
def test_status_update_failure_does_not_rollback_committed_data(
    mock_connection,
):
    connection = MagicMock()
    cursor = MagicMock()

    mock_connection.return_value = connection
    connection.cursor.return_value = cursor

    # Fail only when marking the run SUCCESS.
    def execute_side_effect(query, params=None):
        if params and params[0] == "SUCCESS":
            raise RuntimeError("Status update failed")

    cursor.execute.side_effect = execute_side_effect

    batches = [[make_prediction(101)]]

    with pytest.raises(
        RuntimeError,
        match="Status update failed",
    ):
        save_predictions_in_batches(
            iter(batches),
            batch_size=2,
        )

    connection.commit.assert_called_once()
    connection.rollback.assert_not_called()
    connection.close.assert_called_once()
    cursor.close.assert_called_once()