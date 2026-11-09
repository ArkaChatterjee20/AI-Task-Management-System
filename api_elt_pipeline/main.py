
import logging

from api_elt_pipeline.extract.extractor import extract_tasks
from api_elt_pipeline.load.snowflake_loader import load_tasks_to_snowflake
from api_elt_pipeline.load.sql_runner import run_sql_file
from api_elt_pipeline.state.state_manager import (
    load_processed_ids,
    save_processed_ids,
)
from api_elt_pipeline.state.pending_batch_manager import (
    load_pending_batch,
    save_pending_batch,
    clear_pending_batch,
)
from api_elt_pipeline.storage.raw_storage import (
    load_raw_tasks,
    save_raw_tasks,
)
from api_elt_pipeline.validation.deduplication import (
    filter_new_tasks_with_stats,
)
from api_elt_pipeline.validation.validator import validate_tasks


def configure_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )


def main():
    configure_logging()

    try:
        logging.info("Starting API ELT pipeline.")

        # Initialize execution metrics.
        recovered_batch = False
        extracted_records_count = None
        previously_processed_count = None
        batch_duplicate_count = None
        new_records_count = None

        # STEP 1: Check whether an earlier batch needs recovery.
        pending_file = load_pending_batch()

        if pending_file:
            logging.info(
                "Pending batch found. Recovering RAW data from: %s",
                pending_file,
            )

            file_path = pending_file
            recovered_batch = True

        else:
            # STEP 2: Extract new data.
            tasks = extract_tasks()
            extracted_records_count = len(tasks)

            # STEP 3: Validate extracted data.
            validate_tasks(tasks)

            # STEP 4: Identify new records and collect statistics.
            processed_ids = load_processed_ids()

            deduplication_result = filter_new_tasks_with_stats(
                tasks,
                processed_ids,
            )

            new_tasks = deduplication_result["new_tasks"]

            previously_processed_count = (
                deduplication_result["previously_processed_count"]
            )

            batch_duplicate_count = (
                deduplication_result["batch_duplicate_count"]
            )

            new_records_count = (
                deduplication_result["new_records_count"]
            )

            if not new_tasks:
                logging.info("No new records found.")
                print("\nNo new records to process.")

                return {
                    "status": "NO_NEW_RECORDS",
                    "batch_id": None,
                    "extracted_records_count": extracted_records_count,
                    "previously_processed_count": previously_processed_count,
                    "batch_duplicate_count": batch_duplicate_count,
                    "new_records_count": 0,
                    "loaded_records_count": 0,
                    "recovered_batch": False,
                }

            # STEP 5: Save new records to RAW JSON.
            file_path = save_raw_tasks(new_tasks)

            # STEP 6: Register the batch for recovery.
            save_pending_batch(file_path)

        # STEP 7: Read the RAW JSON batch.
        raw_payload = load_raw_tasks(file_path)

        required_metadata = {
            "batch_id",
            "extracted_at",
            "record_count",
            "data",
        }

        missing_metadata = required_metadata - raw_payload.keys()

        if missing_metadata:
            raise ValueError(
                f"RAW batch is missing metadata: {missing_metadata}"
            )

        saved_tasks = raw_payload["data"]

        if raw_payload["record_count"] != len(saved_tasks):
            raise ValueError(
                "RAW data verification failed: record count does not match."
            )

        if not saved_tasks:
            raise ValueError("RAW batch contains no records.")

        validate_tasks(saved_tasks)

        logging.info(
            "RAW batch verified. Batch ID: %s | Records: %s",
            raw_payload["batch_id"],
            len(saved_tasks),
        )

        # For recovered batches, original extraction and deduplication
        # statistics are unavailable.
        if recovered_batch:
            new_records_count = len(saved_tasks)

        # STEP 8: Load the batch into Snowflake RAW.
        loaded_record_count = load_tasks_to_snowflake(
            tasks=saved_tasks,
            batch_id=raw_payload["batch_id"],
            source_extracted_at=raw_payload["extracted_at"],
        )

        if loaded_record_count != len(saved_tasks):
            raise ValueError(
                "Snowflake load verification failed: "
                "record count does not match."
            )

        logging.info("Snowflake RAW load verification successful.")

        # STEP 9: Transform RAW data into STAGING.
        run_sql_file("snowflake_api_pipeline/03_staging_transform.sql")

        # STEP 10: Update the ANALYTICS layer.
        run_sql_file("snowflake_api_pipeline/04_analytics_transform.sql")

        # STEP 11: Update the processed-record checkpoint.
        processed_ids = load_processed_ids()
        new_ids = {task["id"] for task in saved_tasks}
        processed_ids.update(new_ids)
        save_processed_ids(processed_ids)

        # STEP 12: Clear pending state only after successful completion.
        clear_pending_batch()

        logging.info("API ELT pipeline completed successfully.")

        print("\nELT pipeline completed successfully.")
        print("Batch ID:", raw_payload["batch_id"])
        print("Records loaded:", loaded_record_count)

        # Return structured execution metrics.
        return {
            "status": "SUCCESS",
            "batch_id": raw_payload["batch_id"],
            "extracted_records_count": extracted_records_count,
            "previously_processed_count": previously_processed_count,
            "batch_duplicate_count": batch_duplicate_count,
            "new_records_count": new_records_count,
            "loaded_records_count": loaded_record_count,
            "recovered_batch": recovered_batch,
        }

    except Exception as error:
        logging.exception("Pipeline failed: %s", error)
        raise


if __name__ == "__main__":
    main()
