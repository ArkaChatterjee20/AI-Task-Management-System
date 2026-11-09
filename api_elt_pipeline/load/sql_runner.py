import logging
from pathlib import Path

from api_elt_pipeline.load.snowflake_connection import (
    get_snowflake_connection,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def run_sql_file(file_path: str) -> None:
    """
    Read a SQL file and execute its SQL statement in Snowflake.
    """

    sql_path = PROJECT_ROOT / file_path

    if not sql_path.exists():
        raise FileNotFoundError(
            f"SQL file not found: {sql_path}"
        )

    logging.info(
        "Reading SQL file: %s",
        sql_path,
    )

    sql_query = sql_path.read_text(
        encoding="utf-8"
    ).strip()

    if not sql_query:
        raise ValueError(
            f"SQL file is empty: {sql_path}"
        )

    connection = None
    cursor = None

    try:
        logging.info(
            "Connecting to Snowflake to execute SQL."
        )

        connection = get_snowflake_connection()
        cursor = connection.cursor()

        logging.info(
            "Executing SQL transformation: %s",
            sql_path.name,
        )

        cursor.execute(sql_query, num_statements=1)

        logging.info(
            "SQL transformation completed successfully: %s",
            sql_path.name,
        )

    except Exception as error:

        logging.exception(
            "SQL transformation failed for %s: %s",
            sql_path.name,
            error,
        )

        raise

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()

            logging.info(
                "Snowflake connection closed."
            )