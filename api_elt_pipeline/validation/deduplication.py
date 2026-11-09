
import logging


def filter_new_tasks_with_stats(tasks, processed_ids):
    """
    Filter new and unique tasks and return deduplication statistics.

    Excludes:
    1. IDs already present in the previous checkpoint.
    2. Duplicate IDs within the current extraction batch.

    Returns:
        dict: New tasks and deduplication statistics.
    """

    new_tasks = []

    seen_ids = set(processed_ids)

    previously_processed_count = 0
    batch_duplicate_count = 0

    for task in tasks:

        task_id = task["id"]

        if task_id in seen_ids:

            if task_id in processed_ids:
                previously_processed_count += 1
            else:
                batch_duplicate_count += 1

            continue

        new_tasks.append(task)
        seen_ids.add(task_id)

    new_records_count = len(new_tasks)

    logging.info(
        "New records: %s | Previously processed: %s | "
        "Batch duplicates: %s",
        new_records_count,
        previously_processed_count,
        batch_duplicate_count,
    )

    return {
        "new_tasks": new_tasks,
        "previously_processed_count": previously_processed_count,
        "batch_duplicate_count": batch_duplicate_count,
        "new_records_count": new_records_count,
    }


def filter_new_tasks(tasks, processed_ids):
    """
    Backward-compatible wrapper.

    Returns only the list of new tasks, as before.
    """

    result = filter_new_tasks_with_stats(tasks, processed_ids)

    return result["new_tasks"]
