from api_elt_pipeline.load.snowflake_connection import get_snowflake_connection

conn = None
cur = None

try:
    conn = get_snowflake_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            COUNT(*),
            COUNT(DISTINCT USER_ID),
            COUNT_IF(IS_COMPLETED),
            COUNT_IF(NOT IS_COMPLETED)
        FROM AI_TASK_MANAGEMENT_DB.STAGING.TASKS_STAGING
    """)

    print("STAGING (tasks, users, completed, pending):", cur.fetchone())

    cur.execute("""
        SELECT
            COUNT(*),
            COUNT(DISTINCT USER_ID),
            SUM(TOTAL_TASKS),
            SUM(COMPLETED_TASKS),
            SUM(PENDING_TASKS)
        FROM AI_TASK_MANAGEMENT_DB.ANALYTICS.TASK_SUMMARY
    """)

    print("ANALYTICS (users, distinct users, tasks, completed, pending):", cur.fetchone())

finally:
    if cur:
        cur.close()
    if conn:
        conn.close()
