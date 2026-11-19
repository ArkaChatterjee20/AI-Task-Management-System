
import logging
import os
import re
from pathlib import Path

from api_elt_pipeline.load.snowflake_connection import (
    get_snowflake_connection,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]

IDENTIFIER_PATTERN = r"[A-Za-z_][A-Za-z0-9_$]*"


def get_sql_configuration():
    """Read and validate Snowflake database and schema settings."""

    configuration = {
        "DATABASE": os.getenv("SNOWFLAKE_DATABASE"),
        "RAW_SCHEMA": os.getenv(
            "SNOWFLAKE_RAW_SCHEMA",
            "RAW",
        ),
        "STAGING_SCHEMA": os.getenv(
            "SNOWFLAKE_STAGING_SCHEMA",
            "STAGING",
        ),
        "ANALYTICS_SCHEMA": os.getenv(
            "SNOWFLAKE_ANALYTICS_SCHEMA",
            "ANALYTICS",
        ),
    }

    for name, value in configuration.items():

        if not value:
            raise ValueError(
                f"Snowflake {name} is not configured."
            )

        if not re.fullmatch(
            IDENTIFIER_PATTERN,
            value,
        ):
            raise ValueError(
                f"Invalid Snowflake {name} identifier."
            )

    return configuration


def run_sql_file(file_path: str) -> None:
    """
    Read a SQL file and execute its SQL statement in Snowflake.

    Database and schema placeholders are replaced using
    the configured environment variables.
    """

    configuration = get_sql_configuration()

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

    # Replace database and schema placeholders.
    for placeholder, value in configuration.items():

        sql_query = sql_query.replace(
            "{{" + placeholder + "}}",
            value,
        )

    # Check for unresolved placeholders.
    unresolved_placeholders = re.findall(
        r"\{\{[^{}]+\}\}",
        sql_query,
    )

    if unresolved_placeholders:
        raise ValueError(
            "SQL file contains unresolved placeholders: "
            + ", ".join(unresolved_placeholders)
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

        cursor.execute(
            sql_query,
            num_statements=1,
        )

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
