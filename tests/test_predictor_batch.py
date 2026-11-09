
from unittest.mock import MagicMock, patch

import pytest

from fastapi_backend.ml.predictor import (
    predict_tasks,
    predict_tasks_in_batches,
)


@pytest.fixture
def mock_ml_components():
    vectorizer = MagicMock()
    vectorizer.transform.side_effect = lambda titles: titles

    model = MagicMock()
    model.predict.side_effect = lambda features: [
        1 if title == "Done task" else 0
        for title in features
    ]

    with patch(
        "fastapi_backend.ml.predictor.load_ml_components",
        return_value=(vectorizer, model),
    ):
        with patch(
            "fastapi_backend.ml.predictor.preprocess_text",
            side_effect=lambda text: text,
        ):
            yield vectorizer, model


def test_predictions_are_generated_in_batches(mock_ml_components):
    tasks = [
        {"task_id": 1, "task_title": "Done task"},
        {"task_id": 2, "task_title": "Pending task"},
        {"task_id": 3, "task_title": "Done task"},
    ]

    batches = list(
        predict_tasks_in_batches(tasks, batch_size=2)
    )

    assert len(batches) == 2
    assert len(batches[0]) == 2
    assert len(batches[1]) == 1

    assert batches[0][0]["predicted_status"] == "Done"
    assert batches[0][1]["predicted_status"] == "Not Done"


def test_original_predict_tasks_returns_list(mock_ml_components):
    tasks = [
        {"task_id": 1, "task_title": "Done task"},
        {"task_id": 2, "task_title": "Pending task"},
    ]

    results = predict_tasks(tasks)

    assert isinstance(results, list)
    assert len(results) == 2
    assert results[0]["task_id"] == 1
    assert results[1]["task_id"] == 2


def test_empty_tasks_return_no_batches(mock_ml_components):
    batches = list(predict_tasks_in_batches([], batch_size=2))

    assert batches == []


@pytest.mark.parametrize("batch_size", [0, -1, True, 1.5, "100"])
def test_invalid_batch_size_is_rejected(batch_size):
    with pytest.raises(ValueError):
        list(
            predict_tasks_in_batches(
                [],
                batch_size=batch_size,
            )
        )
