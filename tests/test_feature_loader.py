
from unittest.mock import MagicMock, patch

import pytest

from fastapi_backend.ml.feature_loader import (
    iter_task_features,
    load_task_features,
)


def create_mock_connection(rows):
    connection = MagicMock()
    cursor = MagicMock()

    connection.cursor.return_value = cursor

    batches = [
        rows[index:index + 2]
        for index in range(0, len(rows), 2)
    ]

    cursor.fetchmany.side_effect = batches + [[]]

    return connection, cursor


@patch("fastapi_backend.ml.feature_loader.get_snowflake_connection")
def test_iter_task_features_returns_batches(mock_connection):
    rows = [
        (1, "Task One"),
        (2, "Task Two"),
        (3, "Task Three"),
        (4, "Task Four"),
    ]

    connection, cursor = create_mock_connection(rows)
    mock_connection.return_value = connection

    batches = list(iter_task_features(batch_size=2))

    assert len(batches) == 2
    assert len(batches[0]) == 2
    assert len(batches[1]) == 2

    assert batches[0][0] == {
        "task_id": 1,
        "task_title": "Task One",
    }

    assert cursor.fetchmany.call_count == 3
    cursor.close.assert_called_once()
    connection.close.assert_called_once()


@patch("fastapi_backend.ml.feature_loader.get_snowflake_connection")
def test_iter_task_features_handles_empty_data(mock_connection):
    connection, cursor = create_mock_connection([])
    mock_connection.return_value = connection

    batches = list(iter_task_features(batch_size=2))

    assert batches == []
    cursor.close.assert_called_once()
    connection.close.assert_called_once()


@pytest.mark.parametrize("batch_size", [0, -1, True, 1.5, "100"])
def test_iter_task_features_rejects_invalid_batch_size(batch_size):
    with pytest.raises(ValueError):
        list(iter_task_features(batch_size=batch_size))


@patch("fastapi_backend.ml.feature_loader.get_snowflake_connection")
def test_load_task_features_preserves_list_interface(mock_connection):
    rows = [
        (1, "Task One"),
        (2, "Task Two"),
        (3, "Task Three"),
    ]

    connection, cursor = create_mock_connection(rows)
    mock_connection.return_value = connection

    features = load_task_features()

    assert isinstance(features, list)
    assert len(features) == 3
    assert features[2]["task_title"] == "Task Three"

    cursor.close.assert_called_once()
    connection.close.assert_called_once()
