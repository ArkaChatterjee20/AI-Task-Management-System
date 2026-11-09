
from unittest.mock import patch

from fastapi_backend.routers import ml_predictions


def test_successful_prediction_pipeline():

    feature_batches = [
        [
            {"task_id": 1, "task_title": "Test one"},
            {"task_id": 2, "task_title": "Test two"},
        ],
        [
            {"task_id": 3, "task_title": "Test three"},
        ],
    ]

    prediction_batches = [
        [
            {
                "task_id": 1,
                "task_title": "Test one",
                "prediction": 1,
                "predicted_status": "Done",
            },
            {
                "task_id": 2,
                "task_title": "Test two",
                "prediction": 0,
                "predicted_status": "Not Done",
            },
        ],
        [
            {
                "task_id": 3,
                "task_title": "Test three",
                "prediction": 1,
                "predicted_status": "Done",
            },
        ],
    ]

    # Store the batches consumed by the mock writer.
    captured_batches = []

    def mock_save_predictions(
        batches,
        batch_size=1000,
    ):
        captured_batches.extend(list(batches))
        return "test-prediction-uuid"

    with (
        patch.object(
            ml_predictions,
            "start_pipeline_run",
            return_value=801,
        ) as start,

        patch.object(
            ml_predictions,
            "iter_task_features",
            return_value=iter(feature_batches),
        ) as feature_loader,

        patch.object(
            ml_predictions,
            "predict_tasks_in_batches",
            return_value=iter(prediction_batches),
        ) as predictor,

        patch.object(
            ml_predictions,
            "save_predictions_in_batches",
            side_effect=mock_save_predictions,
        ) as writer,

        patch.object(
            ml_predictions,
            "complete_pipeline_run",
        ) as complete,

        patch.object(
            ml_predictions,
            "fail_pipeline_run",
        ) as fail,
    ):

        response = ml_predictions.get_predictions()

        # Verify API response.
        assert response == {
            "run_id": "test-prediction-uuid",
            "pipeline_run_id": 801,
            "status": "SUCCESS",
            "total_predictions": 3,
        }

        # Full predictions must not be returned.
        assert "predictions" not in response

        # Verify pipeline tracking.
        start.assert_called_once_with(
            "ML_TASK_PREDICTION_PIPELINE"
        )

        # Verify feature extraction.
        feature_loader.assert_called_once_with(
            batch_size=1000
        )

        # Verify predictor invocation.
        predictor.assert_called_once()

        # Verify batch writer invocation.
        writer.assert_called_once()

        # Verify both prediction batches were consumed.
        assert len(captured_batches) == 2

        assert sum(
            len(batch)
            for batch in captured_batches
        ) == 3

        # Verify pipeline completion.
        complete.assert_called_once_with(801, 3)

        # Failure tracking should not be called.
        fail.assert_not_called()


def test_failed_prediction_pipeline():

    with (
        patch.object(
            ml_predictions,
            "start_pipeline_run",
            return_value=802,
        ),

        patch.object(
            ml_predictions,
            "iter_task_features",
            side_effect=RuntimeError(
                "Simulated feature loading failure"
            ),
        ),

        patch.object(
            ml_predictions,
            "fail_pipeline_run",
        ) as fail,
    ):

        try:
            ml_predictions.get_predictions()

            assert False, "Expected HTTPException"

        except Exception as error:
            assert getattr(error, "status_code", None) == 500

        # Verify pipeline failure tracking.
        fail.assert_called_once()

        args = fail.call_args.args

        assert args[0] == 802

        assert (
            "Simulated feature loading failure"
            in args[1]
        )


if __name__ == "__main__":

    test_successful_prediction_pipeline()

    print("SUCCESS PATH TEST PASSED")

    test_failed_prediction_pipeline()

    print("FAILURE PATH TEST PASSED")

    print("\nALL ML PIPELINE TRACKING TESTS PASSED")
