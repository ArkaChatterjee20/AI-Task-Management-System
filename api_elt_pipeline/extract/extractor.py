import logging

from api_elt_pipeline.extract.api_client import get_todos


def extract_tasks():
    """
    Extract task records from the external API.
    """

    logging.info("Starting task extraction.")

    tasks = get_todos()

    if not isinstance(tasks, list):
        raise ValueError(
            "Expected the API response to be a list."
        )

    logging.info(
        "Successfully extracted %s records.",
        len(tasks),
    )

    return tasks