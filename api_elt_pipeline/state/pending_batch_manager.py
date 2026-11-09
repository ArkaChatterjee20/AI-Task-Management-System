
import json
import logging
import os

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

PENDING_BATCH_FILE = (
    PROJECT_ROOT
    / "data"
    / "state"
    / "pending_batch.json"
)


def save_pending_batch(file_path):
    """
    Save the RAW JSON file path for recovery.
    """

    PENDING_BATCH_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    temporary_file = PENDING_BATCH_FILE.with_suffix(".tmp")

    payload = {
        "raw_file_path": str(file_path),
    }

    with open(
        temporary_file,
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(payload, file, indent=4)

        file.flush()
        os.fsync(file.fileno())

    os.replace(
        temporary_file,
        PENDING_BATCH_FILE,
    )

    logging.info(
        "Pending batch saved: %s",
        file_path,
    )


def load_pending_batch():
    """
    Return the pending RAW JSON file path, if one exists.
    """

    if not PENDING_BATCH_FILE.exists():
        return None

    with open(
        PENDING_BATCH_FILE,
        "r",
        encoding="utf-8",
    ) as file:

        payload = json.load(file)

    raw_file_path = Path(payload["raw_file_path"])

    if not raw_file_path.exists():
        raise FileNotFoundError(
            f"Pending RAW file not found: {raw_file_path}"
        )

    logging.info(
        "Recovering pending batch: %s",
        raw_file_path,
    )

    return raw_file_path


def clear_pending_batch():
    """
    Clear pending batch state after successful processing.
    """

    if PENDING_BATCH_FILE.exists():
        PENDING_BATCH_FILE.unlink()

    logging.info("Pending batch state cleared.")
