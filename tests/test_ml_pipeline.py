from fastapi_backend.ml.feature_loader import (
    load_task_features,
)
from fastapi_backend.ml.predictor import (
    predict_tasks,
)


def main():

    # Load features from Snowflake
    tasks = load_task_features()

    print(
        f"Features loaded from Snowflake: {len(tasks)}"
    )

    # Generate ML predictions
    predictions = predict_tasks(tasks)

    print(
        f"Predictions generated: {len(predictions)}"
    )

    # Display first 10 predictions
    for prediction in predictions[:10]:
        print(prediction)


if __name__ == "__main__":
    main()