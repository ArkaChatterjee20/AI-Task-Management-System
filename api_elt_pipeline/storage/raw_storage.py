
import json
import logging
import uuid

from datetime import datetime, timezone
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

RAW_DATA_DIRECTORY = (
    PROJECT_ROOT / "data" / "raw"
)


def save_raw_tasks(tasks):
    """
    Save the original API response with batch metadata.
    """

    RAW_DATA_DIRECTORY.mkdir(
        parents=True,
        exist_ok=True,
    )

    # Generate a unique batch ID.
    batch_id = str(uuid.uuid4())

    # Generate UTC extraction timestamp.
    extracted_at = datetime.now(
        timezone.utc
    )

    timestamp = extracted_at.strftime(
        "%Y%m%d_%H%M%S"
    )

    file_name = (
        f"todos_{timestamp}_{batch_id}.json"
    )

    file_path = (
        RAW_DATA_DIRECTORY / file_name
    )

    raw_payload = {
        "batch_id": batch_id,
        "extracted_at": extracted_at.isoformat(),
        "source": "JSONPlaceholder API /todos",
        "record_count": len(tasks),
        "data": tasks,
    }

    with open(
        file_path,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            raw_payload,
            file,
            indent=4,
        )

    logging.info(
        "RAW data saved. Batch ID: %s | Records: %s",
        batch_id,
        len(tasks),
    )

    return file_path


def load_raw_tasks(file_path):
    """
    Load and return data from a RAW JSON file.
    """

    with open(
        file_path,
        "r",
        encoding="utf-8",
    ) as file:

        raw_payload = json.load(file)

    logging.info(
        "RAW data loaded from: %s",
        file_path,
    )

    return raw_payload
