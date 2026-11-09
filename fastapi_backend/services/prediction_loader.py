import json
import logging
import os
import tempfile
import uuid

from api_elt_pipeline.load.snowflake_connection import (
    get_snowflake_connection,
)

def validate_predictions(predictions):
    """
    Validate prediction input and reject duplicate task IDs.
    """

    if not isinstance(predictions, list):
        raise ValueError("Predictions must be a list.")

    seen_task_ids = set()

    for index, prediction in enumerate(predictions):

        if not isinstance(prediction, dict):
            raise ValueError(
                f"Invalid prediction record at index {index}."
            )

        required_fields = [
            "task_id",
            "task_title",
            "prediction",
            "predicted_status",
        ]

        for field in required_fields:
            if field not in prediction:
                raise ValueError(
                    f"Missing {field} at index {index}."
                )

        task_id = prediction["task_id"]

        if isinstance(task_id, bool) or not isinstance(task_id, int) or task_id <= 0:
            raise ValueError(
                f"Invalid task_id at index {index}."
            )

        if task_id in seen_task_ids:
            raise ValueError(
                f"Duplicate task_id detected: {task_id}"
            )

        seen_task_ids.add(task_id)

        task_title = prediction["task_title"]

        if not isinstance(task_title, str) or not task_title.strip():
            raise ValueError(
                f"Invalid task_title at index {index}."
            )

        prediction_value = prediction["prediction"]

        if (
            isinstance(prediction_value, bool)
            or prediction_value not in (0, 1)
        ):
            raise ValueError(
                f"Invalid prediction value at index {index}. Expected 0 or 1."
            )

        expected_status = (
            "Done" if prediction_value == 1 else "Not Done"
        )

        if prediction["predicted_status"] != expected_status:
            raise ValueError(
                f"Invalid predicted_status at index {index}. "
                f"Expected '{expected_status}'."
            )


def save_predictions(predictions):
    """
    Save ML predictions into Snowflake.

    1. Validate predictions.
    2. Register a RUNNING prediction run.
    3. Insert prediction history and merge latest predictions
       in one transaction.
    4. Mark the run SUCCESS or FAILED.
    """

    validate_predictions(predictions)

    connection = get_snowflake_connection()
    cursor = connection.cursor()

    run_id = str(uuid.uuid4())

    try:
        # STEP 1: Register prediction run.
        # Autocommit is enabled initially, so RUNNING remains durable.
        run_query = """
        INSERT INTO PREDICTION_RUNS (
            RUN_ID,
            TOTAL_PREDICTIONS,
            RUN_STATUS
        )
        VALUES (%s, %s, %s)
        """

        cursor.execute(
            run_query,
            (run_id, len(predictions), "RUNNING")
        )

        # STEP 2: Begin prediction transaction.
        connection.autocommit(False)

        records = [
            (
                prediction["task_id"],
                prediction["task_title"],
                prediction["prediction"],
                prediction["predicted_status"]
            )
            for prediction in predictions
        ]

        # STEP 3: Insert prediction history.
        if records:
            history_query = """
            INSERT INTO TASK_PREDICTION_HISTORY (
                RUN_ID,
                TASK_ID,
                TASK_TITLE,
                PREDICTION,
                PREDICTED_STATUS
            )
            VALUES (%s, %s, %s, %s, %s)
            """

            history_records = [
                (run_id, *record)
                for record in records
            ]

            cursor.executemany(
                history_query,
                history_records
            )

        # STEP 4: Merge latest predictions.
        merge_query = """
        MERGE INTO TASK_PREDICTIONS AS target
        USING (
            SELECT
                %s AS TASK_ID,
                %s AS TASK_TITLE,
                %s AS PREDICTION,
                %s AS PREDICTED_STATUS
        ) AS source
        ON target.TASK_ID = source.TASK_ID

        WHEN MATCHED THEN
            UPDATE SET
                TASK_TITLE = source.TASK_TITLE,
                PREDICTION = source.PREDICTION,
                PREDICTED_STATUS = source.PREDICTED_STATUS,
                PREDICTED_AT = CURRENT_TIMESTAMP()

        WHEN NOT MATCHED THEN
            INSERT (
                TASK_ID,
                TASK_TITLE,
                PREDICTION,
                PREDICTED_STATUS
            )
            VALUES (
                source.TASK_ID,
                source.TASK_TITLE,
                source.PREDICTION,
                source.PREDICTED_STATUS
            )
        """

        if records:
            cursor.executemany(merge_query, records)

        # STEP 5: Commit both prediction writes together.
        connection.commit()

        # STEP 6: Restore autocommit before updating run status.
        connection.autocommit(True)

        update_run_query = """
        UPDATE PREDICTION_RUNS
        SET
            RUN_STATUS = %s,
            COMPLETED_AT = CURRENT_TIMESTAMP()
        WHERE RUN_ID = %s
        """

        cursor.execute(
            update_run_query,
            ("SUCCESS", run_id)
        )

        print(f"Prediction Run ID: {run_id}")
        print(f"Predictions merged into Snowflake: {len(records)}")
        print("Prediction run completed successfully.")

        return run_id

    except Exception as e:

        # Roll back any uncommitted prediction writes.
        try:
            connection.rollback()
        except Exception:
            logging.exception("Prediction transaction rollback failed.")

        # Restore autocommit before updating run status.
        try:
            connection.autocommit(True)

            cursor.execute(
                """
                UPDATE PREDICTION_RUNS
                SET
                    RUN_STATUS = %s,
                    COMPLETED_AT = CURRENT_TIMESTAMP()
                WHERE RUN_ID = %s
                """,
                ("FAILED", run_id)
            )

        except Exception:
            logging.exception("Could not mark prediction run as FAILED.")

        logging.exception("Prediction pipeline failed.")
        raise

    finally:
           try:
               cursor.close()
           except Exception:
               logging.exception("Failed to close Snowflake cursor.")

           try:
               connection.close()
           except Exception:
               logging.exception("Failed to close Snowflake connection.")

def validate_prediction_batches(prediction_batches):
    """
    Validate prediction batches and reject duplicate task IDs
    across the entire prediction run.

    Only task IDs are retained between batches.
    """

    if not hasattr(prediction_batches, "__iter__"):
        raise ValueError("Prediction batches must be iterable.")

    seen_task_ids = set()
    total_predictions = 0

    for batch_index, batch in enumerate(prediction_batches):

        validate_predictions(batch)

        for prediction in batch:
            task_id = prediction["task_id"]

            if task_id in seen_task_ids:
                raise ValueError(
                    f"Duplicate task_id across batches: {task_id}"
                )

            seen_task_ids.add(task_id)
            total_predictions += 1

    return total_predictions


def save_predictions_in_batches(prediction_batches, batch_size=1000):
    """
    Validate and save predictions incrementally.
    Uses a temporary JSONL file to avoid retaining all
    prediction records in memory.
    All Snowflake prediction writes share one transaction.
    """

    if (
        not isinstance(batch_size, int)
        or isinstance(batch_size, bool)
        or batch_size <= 0
    ):
        raise ValueError("batch_size must be a positive integer.")

    if not hasattr(prediction_batches, "__iter__"):
        raise ValueError("Prediction batches must be iterable.")

    seen_task_ids = set()
    total_predictions = 0
    run_id = str(uuid.uuid4())

    connection = None
    cursor = None
    data_committed = False
    temp_path = None

    try:
        # PHASE 1: Validate and buffer batches on disk.
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            suffix=".jsonl",
            delete=False,
        ) as temp_file:

            temp_path = temp_file.name

            for batch in prediction_batches:

                validate_predictions(batch)

                if len(batch) > batch_size:
                    raise ValueError(
                        "Prediction batch exceeds batch_size."
                    )

                for prediction in batch:
                    task_id = prediction["task_id"]

                    if task_id in seen_task_ids:
                        raise ValueError(
                            f"Duplicate task_id across batches: {task_id}"
                        )

                    seen_task_ids.add(task_id)

                for prediction in batch:
                    temp_file.write(
                        json.dumps(prediction) + "\n"
                    )

                total_predictions += len(batch)

        # PHASE 2: Connect to Snowflake after validation.
        connection = get_snowflake_connection()
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO PREDICTION_RUNS (
                RUN_ID,
                TOTAL_PREDICTIONS,
                RUN_STATUS
            )
            VALUES (%s, %s, %s)
            """,
            (run_id, total_predictions, "RUNNING"),
        )

        connection.autocommit(False)

        history_query = """
        INSERT INTO TASK_PREDICTION_HISTORY (
            RUN_ID,
            TASK_ID,
            TASK_TITLE,
            PREDICTION,
            PREDICTED_STATUS
        )
        VALUES (%s, %s, %s, %s, %s)
        """

        merge_query = """
        MERGE INTO TASK_PREDICTIONS AS target
        USING (
            SELECT
                %s AS TASK_ID,
                %s AS TASK_TITLE,
                %s AS PREDICTION,
                %s AS PREDICTED_STATUS
        ) AS source
        ON target.TASK_ID = source.TASK_ID

        WHEN MATCHED THEN
            UPDATE SET
                TASK_TITLE = source.TASK_TITLE,
                PREDICTION = source.PREDICTION,
                PREDICTED_STATUS = source.PREDICTED_STATUS,
                PREDICTED_AT = CURRENT_TIMESTAMP()

        WHEN NOT MATCHED THEN
            INSERT (
                TASK_ID,
                TASK_TITLE,
                PREDICTION,
                PREDICTED_STATUS
            )
            VALUES (
                source.TASK_ID,
                source.TASK_TITLE,
                source.PREDICTION,
                source.PREDICTED_STATUS
            )
        """

        # PHASE 3: Read and write one batch at a time.
        with open(temp_path, "r", encoding="utf-8") as temp_file:

            while True:
                batch = []

                for _ in range(batch_size):
                    line = temp_file.readline()

                    if not line:
                        break

                    batch.append(json.loads(line))

                if not batch:
                    break

                records = [
                    (
                        item["task_id"],
                        item["task_title"],
                        item["prediction"],
                        item["predicted_status"],
                    )
                    for item in batch
                ]

                history_records = [
                    (run_id, *record)
                    for record in records
                ]

                cursor.executemany(
                    history_query,
                    history_records,
                )

                cursor.executemany(
                    merge_query,
                    records,
                )

        # PHASE 4: Commit prediction data.
        connection.commit()
        data_committed = True

        # PHASE 5: Mark the run SUCCESS.
        connection.autocommit(True)

        cursor.execute(
            """
            UPDATE PREDICTION_RUNS
            SET
                RUN_STATUS = %s,
                COMPLETED_AT = CURRENT_TIMESTAMP()
            WHERE RUN_ID = %s
            """,
            ("SUCCESS", run_id),
        )

        # FIX 1: Verify that exactly one row was updated.
        if cursor.rowcount != 1:
            raise RuntimeError(
                f"Could not mark prediction run {run_id} as SUCCESS. "
                f"Rows updated: {cursor.rowcount}"
            )

        logging.info(
            "Prediction run %s completed with %s predictions.",
            run_id,
            total_predictions,
        )

        return run_id

    except Exception:

        if connection is not None and not data_committed:

            try:
                connection.rollback()
            except Exception:
                logging.exception("Prediction rollback failed.")

            try:
                connection.autocommit(True)

                if cursor is not None:
                    cursor.execute(
                        """
                        UPDATE PREDICTION_RUNS
                        SET
                            RUN_STATUS = %s,
                            COMPLETED_AT = CURRENT_TIMESTAMP()
                        WHERE RUN_ID = %s
                        """,
                        ("FAILED", run_id),
                    )

            except Exception:
                logging.exception(
                    "Could not mark prediction run as FAILED."
                )

        elif data_committed:
            logging.exception(
                "Prediction data committed, but run status update failed. "
                "Run ID: %s",
                run_id,
            )

        logging.exception("Batch prediction writer failed.")
        raise

    finally:

        if cursor is not None:
            try:
                cursor.close()
            except Exception:
                logging.exception("Cursor close failed.")

        if connection is not None:
            try:
                connection.close()
            except Exception:
                logging.exception("Connection close failed.")

        if temp_path is not None:
            try:
                os.remove(temp_path)
            except OSError:
                logging.exception(
                    "Could not remove temporary prediction file."
                )
