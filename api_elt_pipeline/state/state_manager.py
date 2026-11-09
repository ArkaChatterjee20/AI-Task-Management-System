
import json
import logging
import os
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

STATE_FILE = (
    PROJECT_ROOT
    / "data"
    / "state"
    / "processed_task_ids.json"
)


def load_processed_ids():
    """
    Load IDs of records that have already been processed.
    """

    if not STATE_FILE.exists():
        logging.info(
            "No existing state file found. Starting with an empty state."
        )
        return set()

    with open(STATE_FILE, "r", encoding="utf-8") as file:
        processed_ids = json.load(file)

    if not isinstance(processed_ids, list):
        raise ValueError("Checkpoint must contain a JSON list.")

    for task_id in processed_ids:
        if (
            not isinstance(task_id, int)
            or isinstance(task_id, bool)
            or task_id <= 0
        ):
            raise ValueError(
                f"Invalid task ID found in checkpoint: {task_id}"
            )

    logging.info(
        "Loaded %s processed IDs from state.",
        len(processed_ids),
    )

    return set(processed_ids)


def save_processed_ids(processed_ids):
    """
    Save processed IDs atomically to the state file.
    """

    STATE_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    validated_ids = set(processed_ids)

    for task_id in validated_ids:
        if (
            not isinstance(task_id, int)
            or isinstance(task_id, bool)
            or task_id <= 0
        ):
            raise ValueError(
                f"Invalid task ID cannot be saved: {task_id}"
            )

    temporary_file = STATE_FILE.with_suffix(".tmp")

    try:
        with open(
            temporary_file,
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                sorted(validated_ids),
                file,
                indent=4,
            )

            file.flush()
            os.fsync(file.fileno())

        os.replace(
            temporary_file,
            STATE_FILE,
        )

        logging.info(
            "Atomically saved %s processed IDs to state.",
            len(validated_ids),
        )

    finally:
        if temporary_file.exists():
            temporary_file.unlink()
