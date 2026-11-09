import logging

from api_elt_pipeline.load.sql_runner import (
    run_sql_file,
)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)


def test_sql_runner():

    run_sql_file(
        "snowflake_api_pipeline/03_staging_transform.sql"
    )

    print(
        "STAGING SQL transformation executed successfully."
    )

    run_sql_file(
        "snowflake_api_pipeline/04_analytics_transform.sql"
    )

    print(
        "ANALYTICS SQL transformation executed successfully."
    )


if __name__ == "__main__":
    test_sql_runner()