from api_elt_pipeline.load.snowflake_connection import (
    get_snowflake_connection
)


def get_prediction_summary():

    connection = get_snowflake_connection()
    cursor = connection.cursor()

    try:
        query = """
        SELECT
            COUNT(*) AS total_predictions,
            SUM(
                CASE
                    WHEN PREDICTED_STATUS = 'Done' THEN 1
                    ELSE 0
                END
            ) AS done_predictions,
            SUM(
                CASE
                    WHEN PREDICTED_STATUS = 'Not Done' THEN 1
                    ELSE 0
                END
            ) AS not_done_predictions
        FROM TASK_PREDICTIONS
        """

        cursor.execute(query)

        result = cursor.fetchone()

        total = result[0] or 0
        done = result[1] or 0
        not_done = result[2] or 0

        completion_percentage = (
            round((done / total) * 100, 2)
            if total > 0
            else 0
        )

        return {
            "total_predictions": total,
            "done_predictions": done,
            "not_done_predictions": not_done,
            "completion_percentage": completion_percentage
        }

    finally:
        cursor.close()
        connection.close()