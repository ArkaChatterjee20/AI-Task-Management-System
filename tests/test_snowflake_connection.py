from api_elt_pipeline.load.snowflake_connection import (
    get_snowflake_connection,
)


def test_connection():

    connection = None
    cursor = None

    try:

        connection = get_snowflake_connection()

        cursor = connection.cursor()

        cursor.execute(
            "SELECT CURRENT_VERSION()"
        )

        result = cursor.fetchone()

        print(
            "Snowflake connection successful!"
        )

        print(
            f"Snowflake version: {result[0]}"
        )

    finally:

        if cursor:
            cursor.close()

        if connection:
            connection.close()

            print(
                "Snowflake connection closed."
            )


if __name__ == "__main__":
    test_connection()