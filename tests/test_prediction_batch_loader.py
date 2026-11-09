
import pytest

from fastapi_backend.services.prediction_loader import (
    validate_predictions,
    validate_prediction_batches,
)

def make_prediction(task_id):
    return {
        "task_id": task_id,
        "task_title": f"Task {task_id}",
        "prediction": 1,
        "predicted_status": "Done",
    }


def test_valid_prediction_batch():
    predictions = [
        make_prediction(101),
        make_prediction(102),
    ]

    validate_predictions(predictions)


def test_duplicate_task_ids_in_same_batch_are_rejected():
    predictions = [
        make_prediction(101),
        make_prediction(101),
    ]

    with pytest.raises(
        ValueError,
        match="Duplicate task_id detected: 101",
    ):
        validate_predictions(predictions)


def test_invalid_prediction_batch_is_rejected():
    predictions = [
        make_prediction(101),
        {
            "task_id": 102,
            "task_title": "Invalid task",
            "prediction": 5,
            "predicted_status": "Done",
        },
    ]

    with pytest.raises(ValueError):
        validate_predictions(predictions)


def test_prediction_batches_can_be_validated_individually():
    first_batch = [
        make_prediction(101),
        make_prediction(102),
    ]

    second_batch = [
        make_prediction(103),
        make_prediction(104),
    ]

    validate_predictions(first_batch)
    validate_predictions(second_batch)



def test_duplicate_task_ids_across_batches_are_rejected():
    batches = [
        [
            make_prediction(101),
            make_prediction(102),
        ],
        [
            make_prediction(102),
            make_prediction(103),
        ],
    ]

    with pytest.raises(
        ValueError,
        match="Duplicate task_id across batches: 102",
    ):
        validate_prediction_batches(batches)


def test_batch_validator_returns_total_prediction_count():
    batches = [
        [make_prediction(101), make_prediction(102)],
        [make_prediction(103)],
    ]

    total = validate_prediction_batches(batches)

    assert total == 3
