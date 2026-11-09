from fastapi_backend.services.prediction_analytics import (
    get_prediction_summary,
)


def test_prediction_summary_returns_expected_type():

    summary = get_prediction_summary()

    assert isinstance(summary, (dict, list))


def test_prediction_summary_is_not_none():

    summary = get_prediction_summary()

    assert summary is not None

    print("Prediction Analytics Summary:")
    print(summary)