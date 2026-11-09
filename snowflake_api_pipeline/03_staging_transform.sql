MERGE INTO AI_TASK_MANAGEMENT_DB.STAGING.TASKS_STAGING AS target
USING (

    SELECT
        TASK_ID,
        USER_ID,
        TASK_TITLE,
        COMPLETION_STATUS,
        IS_COMPLETED,
        EXTRACTED_AT,
        TRANSFORMED_AT

    FROM (

        SELECT
            TASK_ID,
            USER_ID,
            TITLE AS TASK_TITLE,

            CASE
                WHEN COMPLETED = TRUE THEN 'COMPLETED'
                ELSE 'PENDING'
            END AS COMPLETION_STATUS,

            COMPLETED AS IS_COMPLETED,
            EXTRACTED_AT,
            CURRENT_TIMESTAMP() AS TRANSFORMED_AT,

            ROW_NUMBER() OVER (
                PARTITION BY TASK_ID
                ORDER BY EXTRACTED_AT DESC
            ) AS ROW_NUM

        FROM AI_TASK_MANAGEMENT_DB.RAW.TASKS_RAW

    ) AS ranked_tasks

    WHERE ROW_NUM = 1

) AS source

ON target.TASK_ID = source.TASK_ID

WHEN MATCHED THEN
    UPDATE SET
        USER_ID = source.USER_ID,
        TASK_TITLE = source.TASK_TITLE,
        COMPLETION_STATUS = source.COMPLETION_STATUS,
        IS_COMPLETED = source.IS_COMPLETED,
        EXTRACTED_AT = source.EXTRACTED_AT,
        TRANSFORMED_AT = source.TRANSFORMED_AT

WHEN NOT MATCHED THEN
    INSERT (
        TASK_ID,
        USER_ID,
        TASK_TITLE,
        COMPLETION_STATUS,
        IS_COMPLETED,
        EXTRACTED_AT,
        TRANSFORMED_AT
    )
    VALUES (
        source.TASK_ID,
        source.USER_ID,
        source.TASK_TITLE,
        source.COMPLETION_STATUS,
        source.IS_COMPLETED,
        source.EXTRACTED_AT,
        source.TRANSFORMED_AT
    );