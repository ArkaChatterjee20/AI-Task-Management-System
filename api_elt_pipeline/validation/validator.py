
import logging


REQUIRED_FIELDS = {
    "userId",
    "id",
    "title",
    "completed",
}


def validate_tasks(tasks):
    """
    Validate the structure and data types of extracted task records.
    Duplicate handling is performed by the deduplication module.
    """

    logging.info("Starting task validation.")

    if not isinstance(tasks, list):
        raise TypeError("Tasks must be provided as a list.")

    if not tasks:
        raise ValueError("No task records were extracted.")

    for index, task in enumerate(tasks):

        if not isinstance(task, dict):
            raise TypeError(
                f"Record at index {index} is not a dictionary."
            )

        missing_fields = REQUIRED_FIELDS - task.keys()

        if missing_fields:
            raise ValueError(
                f"Record at index {index} is missing fields: "
                f"{missing_fields}"
            )

        if (
            not isinstance(task["id"], int)
            or isinstance(task["id"], bool)
            or task["id"] <= 0
        ):
            raise ValueError(
                f"Record at index {index} has an invalid task ID."
            )

        if (
            not isinstance(task["userId"], int)
            or isinstance(task["userId"], bool)
            or task["userId"] <= 0
        ):
            raise ValueError(
                f"Record at index {index} has an invalid user ID."
            )

        if (
            not isinstance(task["title"], str)
            or not task["title"].strip()
        ):
            raise ValueError(
                f"Record at index {index} has an invalid title."
            )

        if not isinstance(task["completed"], bool):
            raise ValueError(
                f"Record at index {index} has an invalid completed value."
            )

    logging.info(
        "Validation successful. %s records validated.",
        len(tasks),
    )

    return True
