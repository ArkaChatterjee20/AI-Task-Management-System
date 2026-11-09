MERGE INTO AI_TASK_MANAGEMENT_DB.ANALYTICS.TASK_SUMMARY AS target
USING (
    SELECT
        USER_ID,
        COUNT(*) AS TOTAL_TASKS,

        SUM(
            CASE
                WHEN IS_COMPLETED THEN 1
                ELSE 0
            END
        ) AS COMPLETED_TASKS,

        SUM(
            CASE
                WHEN NOT IS_COMPLETED THEN 1
                ELSE 0
            END
        ) AS PENDING_TASKS,

        ROUND(
            (
                SUM(
                    CASE
                        WHEN IS_COMPLETED THEN 1
                        ELSE 0
                    END
                ) * 100.0
            ) / COUNT(*),
            2
        ) AS COMPLETION_RATE

    FROM AI_TASK_MANAGEMENT_DB.STAGING.TASKS_STAGING
    GROUP BY USER_ID
) AS source
ON target.USER_ID = source.USER_ID

WHEN MATCHED THEN UPDATE SET
    target.TOTAL_TASKS = source.TOTAL_TASKS,
    target.COMPLETED_TASKS = source.COMPLETED_TASKS,
    target.PENDING_TASKS = source.PENDING_TASKS,
    target.COMPLETION_RATE = source.COMPLETION_RATE,
    target.LAST_UPDATED = CURRENT_TIMESTAMP()

WHEN NOT MATCHED THEN INSERT (
    USER_ID,
    TOTAL_TASKS,
    COMPLETED_TASKS,
    PENDING_TASKS,
    COMPLETION_RATE,
    LAST_UPDATED
)
VALUES (
    source.USER_ID,
    source.TOTAL_TASKS,
    source.COMPLETED_TASKS,
    source.PENDING_TASKS,
    source.COMPLETION_RATE,
    CURRENT_TIMESTAMP()
);