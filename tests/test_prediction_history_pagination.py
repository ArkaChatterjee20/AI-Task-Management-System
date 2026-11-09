
from unittest.mock import MagicMock, patch

import pytest

from fastapi_backend.services.prediction_history import (
    get_prediction_history_paginated,
)


@patch(
    "fastapi_backend.services.prediction_history.get_snowflake_connection"
)
def test_prediction_history_returns_paginated_results(mock_connection):
    connection = MagicMock()
    cursor = MagicMock()

    mock_connection.return_value = connection
    connection.cursor.return_value = cursor

    cursor.fetchone.return_value = (250,)
    cursor.description = [
        ("RUN_ID",),
        ("TASK_ID",),
        ("TASK_TITLE",),
        ("PREDICTION",),
        ("PREDICTED_STATUS",),
        ("PREDICTED_AT",),
    ]

    cursor.fetchall.return_value = [
        ("run-123", 101, "Task 101", 1, "Done", None),
        ("run-123", 102, "Task 102", 0, "Not Done", None),
    ]

    result = get_prediction_history_paginated(
        run_id="run-123",
        page=2,
        page_size=100,
    )

    assert result["total_records"] == 250
    assert result["page"] == 2
    assert result["page_size"] == 100
    assert result["total_pages"] == 3
    assert len(result["predictions"]) == 2

    assert cursor.execute.call_count == 2
    assert cursor.execute.call_args.args[1] == (
        "run-123",
        100,
        100,
    )

    cursor.close.assert_called_once()
    connection.close.assert_called_once()


@pytest.mark.parametrize(
    "page,page_size",
    [
        (0, 100),
        (-1, 100),
        (True, 100),
        (1, 0),
        (1, 1001),
        (1, True),
    ],
)
def test_prediction_history_rejects_invalid_pagination(
    page,
    page_size,
):
    with pytest.raises(ValueError):
        get_prediction_history_paginated(
            "run-123",
            page=page,
            page_size=page_size,
        )
