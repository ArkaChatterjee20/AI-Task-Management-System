from unittest.mock import MagicMock, patch

from fastapi_backend.services.prediction_loader import save_predictions


def test_save_predictions_returns_run_id():

    predictions = [
        {
            "task_id": 9991,
            "task_title": "Test task",
            "prediction": 1,
            "predicted_status": "Done",
        }
    ]

    mock_connection = MagicMock()
    mock_cursor = MagicMock()

    mock_connection.cursor.return_value = mock_cursor

    with patch(
        "fastapi_backend.services.prediction_loader.get_snowflake_connection",
        return_value=mock_connection,
    ):

        run_id = save_predictions(predictions)

    assert isinstance(run_id, str)
    assert len(run_id) == 36

    assert mock_cursor.execute.call_count == 2
    assert mock_cursor.executemany.call_count == 2

    assert mock_connection.commit.call_count == 1

    assert mock_connection.autocommit.call_args_list == [
        ((False,),),
        ((True,),),
    ]

    mock_cursor.close.assert_called_once()
    mock_connection.close.assert_called_once()


def test_save_predictions_with_empty_list():

    mock_connection = MagicMock()
    mock_cursor = MagicMock()

    mock_connection.cursor.return_value = mock_cursor

    with patch(
        "fastapi_backend.services.prediction_loader.get_snowflake_connection",
        return_value=mock_connection,
    ):

        run_id = save_predictions([])

    assert isinstance(run_id, str)

    assert mock_cursor.execute.call_count == 2
    mock_cursor.executemany.assert_not_called()

    mock_connection.close.assert_called_once()
def test_duplicate_task_ids_are_rejected_before_database_connection():

    predictions = [
        {
            "task_id": 101,
            "task_title": "Complete project",
            "prediction": 1,
            "predicted_status": "Done",
        },
        {
            "task_id": 101,
            "task_title": "Complete project",
            "prediction": 0,
            "predicted_status": "Not Done",
        },
    ]

    with patch(
        "fastapi_backend.services.prediction_loader.get_snowflake_connection"
    ) as mock_connection:

        try:
            save_predictions(predictions)
            assert False, "Expected duplicate task ID to be rejected"

        except ValueError as error:
            assert "Duplicate task_id detected: 101" in str(error)

        mock_connection.assert_not_called()

def test_prediction_failure_rolls_back_and_marks_run_failed():

    predictions = [
        {
            "task_id": 5001,
            "task_title": "Test transaction failure",
            "prediction": 1,
            "predicted_status": "Done",
        }
    ]

    mock_connection = MagicMock()
    mock_cursor = MagicMock()
    mock_connection.cursor.return_value = mock_cursor

    # Fail during history insertion.
    mock_cursor.executemany.side_effect = RuntimeError(
        "Simulated Snowflake history insertion failure"
    )

    with patch(
        "fastapi_backend.services.prediction_loader.get_snowflake_connection",
        return_value=mock_connection,
    ):

        try:
            save_predictions(predictions)
            assert False, "Expected transaction failure"

        except RuntimeError as error:
            assert "Simulated Snowflake history insertion failure" in str(error)

    mock_connection.rollback.assert_called_once()

    # The loader attempts to mark the run as FAILED.
    assert mock_cursor.execute.call_count == 2

    failed_update = mock_cursor.execute.call_args_list[1]
    assert failed_update.args[1][0] == "FAILED"

    mock_cursor.close.assert_called_once()
    mock_connection.close.assert_called_once()

def test_missing_task_title_is_rejected_before_database_connection():

    predictions = [
        {
            "task_id": 6001,
            "prediction": 1,
            "predicted_status": "Done",
        }
    ]

    with patch(
        "fastapi_backend.services.prediction_loader.get_snowflake_connection"
    ) as mock_connection:

        try:
            save_predictions(predictions)
            assert False, "Expected missing title to be rejected"

        except ValueError as error:
            assert "task_title" in str(error)

        mock_connection.assert_not_called()


def test_invalid_prediction_value_is_rejected_before_database_connection():

    predictions = [
        {
            "task_id": 6002,
            "task_title": "Test task",
            "prediction": 5,
            "predicted_status": "Done",
        }
    ]

    with patch(
        "fastapi_backend.services.prediction_loader.get_snowflake_connection"
    ) as mock_connection:

        try:
            save_predictions(predictions)
            assert False, "Expected invalid prediction to be rejected"

        except ValueError:
            pass

        mock_connection.assert_not_called()

