
import os
import requests
import pandas as pd
import streamlit as st


# =====================================================
# PAGE CONFIGURATION
# =====================================================

st.set_page_config(
    page_title="ELT Pipeline Dashboard",
    page_icon="📊",
    layout="wide",
)


# =====================================================
# CONFIGURATION
# =====================================================

API_BASE_URL = os.getenv(
    "API_BASE_URL",
    "http://api:8000",
).rstrip("/")

PIPELINE_RUN_URL = f"{API_BASE_URL}/pipeline/run"
PIPELINE_HISTORY_URL = f"{API_BASE_URL}/pipeline/runs"

REQUEST_TIMEOUT = 300


# =====================================================
# CUSTOM CSS
# =====================================================

st.markdown(
    """
    <style>

    [data-testid="stAppViewContainer"] {
        background-color: #0f172a;
        color: #f8fafc;
    }

    [data-testid="stHeader"] {
        background-color: #0f172a;
    }

    [data-testid="stSidebar"] {
        background-color: #1e293b;
    }

    .main .block-container {
        color: #f8fafc;
        padding-top: 2rem;
    }

    .dashboard-header {
        font-size: 34px;
        font-weight: bold;
        color: #f8fafc;
    }

    .dashboard-subtitle {
        color: #94a3b8;
        font-size: 15px;
    }

    h1, h2, h3, h4 {
        color: #f8fafc !important;
    }

    div[data-testid="stMetric"] {
        background-color: #1e293b;
        padding: 18px;
        border-radius: 12px;
        border: 1px solid #334155;
    }

    div[data-testid="stMetricLabel"],
    div[data-testid="stMetricLabel"] p {
        color: #cbd5e1 !important;
    }

    div[data-testid="stMetricValue"] {
        color: #f8fafc !important;
    }

    .stMarkdown p,
    .stCaption {
        color: #cbd5e1;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# =====================================================
# SESSION STATE
# =====================================================

if "pipeline_result" not in st.session_state:
    st.session_state.pipeline_result = None

if "pipeline_error" not in st.session_state:
    st.session_state.pipeline_error = None


# =====================================================
# EXECUTE ELT PIPELINE
# =====================================================

def execute_pipeline():

    try:

        response = requests.post(
            PIPELINE_RUN_URL,
            timeout=REQUEST_TIMEOUT,
        )

        response.raise_for_status()

        result = response.json()

        st.session_state.pipeline_result = result
        st.session_state.pipeline_error = None

        return result

    except requests.exceptions.Timeout:

        st.session_state.pipeline_error = (
            "The pipeline request timed out. "
            "Check the API logs before retrying because "
            "the pipeline may still have executed."
        )

    except requests.exceptions.ConnectionError:

        st.session_state.pipeline_error = (
            "Cannot connect to FastAPI. "
            "Check whether the API container is running."
        )

    except requests.exceptions.HTTPError:

        try:
            error_detail = response.json().get(
                "detail",
                response.text,
            )

        except Exception:
            error_detail = response.text

        st.session_state.pipeline_error = (
            f"Pipeline API returned HTTP "
            f"{response.status_code}: {error_detail}"
        )

    except requests.exceptions.RequestException as error:

        st.session_state.pipeline_error = str(error)

    except ValueError:

        st.session_state.pipeline_error = (
            "The API returned an invalid JSON response."
        )

    return None


# =====================================================
# FETCH PIPELINE EXECUTION HISTORY
# =====================================================

def fetch_pipeline_history(limit=20, offset=0):

    try:

        response = requests.get(
            PIPELINE_HISTORY_URL,
            params={
                "limit": limit,
                "offset": offset,
            },
            timeout=30,
        )

        response.raise_for_status()

        return response.json()

    except requests.exceptions.HTTPError:

        try:
            error_detail = response.json().get(
                "detail",
                response.text,
            )

        except Exception:
            error_detail = response.text

        st.error(
            f"Pipeline history API returned HTTP "
            f"{response.status_code}: {error_detail}"
        )

    except requests.exceptions.ConnectionError:

        st.error(
            "Cannot connect to the FastAPI pipeline history endpoint."
        )

    except requests.exceptions.Timeout:

        st.error(
            "Pipeline history request timed out."
        )

    except requests.exceptions.RequestException as error:

        st.error(
            f"Unable to fetch pipeline history: {error}"
        )

    except ValueError:

        st.error(
            "The pipeline history API returned invalid JSON."
        )

    return None


# =====================================================
# DASHBOARD HEADER
# =====================================================

st.markdown(
    '<div class="dashboard-header">'
    '📊 ELT Pipeline Dashboard'
    '</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="dashboard-subtitle">'
    'Monitor extraction, validation, loading and transformation.'
    '</div>',
    unsafe_allow_html=True,
)

st.divider()


# =====================================================
# PIPELINE EXECUTION
# =====================================================

st.subheader("Pipeline Execution")

col1, col2 = st.columns([2, 1])

with col1:

    st.write(
        "Execute the API ELT pipeline and load new records "
        "into the Snowflake data warehouse."
    )

with col2:

    run_clicked = st.button(
        "▶ Run ELT Pipeline",
        type="primary",
        use_container_width=True,
    )


if run_clicked:

    with st.spinner(
        "Executing ELT pipeline. Please wait..."
    ):

        execute_pipeline()


if st.session_state.pipeline_error:

    st.error(
        st.session_state.pipeline_error
    )


result = st.session_state.pipeline_result


# =====================================================
# PIPELINE OVERVIEW
# =====================================================

st.divider()

st.subheader("Pipeline Overview")

if result:

    status = result.get(
        "status",
        "UNKNOWN",
    )

    col1, col2 = st.columns([2, 1])

    with col1:

        if status == "SUCCESS":

            st.success(
                "ELT pipeline completed successfully."
            )

        elif status == "NO_NEW_RECORDS":

            st.info(
                "Pipeline completed. No new records "
                "were available for processing."
            )

        else:

            st.warning(
                f"Pipeline returned status: {status}"
            )

    with col2:

        st.metric(
            "Pipeline Status",
            status,
        )

else:

    col1, col2 = st.columns([2, 1])

    with col1:

        st.info(
            "Click 'Run ELT Pipeline' to execute the "
            "pipeline and retrieve actual execution metrics."
        )

    with col2:

        st.metric(
            "Pipeline Status",
            "Not executed",
        )


# =====================================================
# EXECUTION METRICS
# =====================================================

st.divider()

st.subheader("Execution Metrics")

if result:

    extracted = result.get(
        "extracted_records_count"
    )

    new_records = result.get(
        "new_records_count"
    )

    duplicates = result.get(
        "batch_duplicate_count"
    )

    loaded = result.get(
        "loaded_records_count"
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:

        st.metric(
            "Extracted Records",
            extracted if extracted is not None else "N/A",
        )

    with col2:

        st.metric(
            "New Records",
            new_records if new_records is not None else "N/A",
        )

    with col3:

        st.metric(
            "Batch Duplicates",
            duplicates if duplicates is not None else "N/A",
        )

    with col4:

        st.metric(
            "Loaded Records",
            loaded if loaded is not None else "N/A",
        )

    st.caption(
        "N/A means the pipeline did not return that metric, "
        "such as during batch recovery."
    )

else:

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Extracted Records", "—")

    with col2:
        st.metric("New Records", "—")

    with col3:
        st.metric("Batch Duplicates", "—")

    with col4:
        st.metric("Loaded Records", "—")


# =====================================================
# SNOWFLAKE DATA WAREHOUSE
# =====================================================

st.divider()

st.subheader("Snowflake Data Warehouse")

raw_col, staging_col, analytics_col = st.columns(3)

pipeline_status = (
    result.get("status")
    if result
    else None
)


with raw_col:

    st.markdown("### RAW")

    st.caption(
        "Source data ingestion"
    )

    if pipeline_status == "SUCCESS":

        st.success(
            "RAW data loaded successfully."
        )

    elif pipeline_status == "NO_NEW_RECORDS":

        st.info(
            "Skipped — no new records available."
        )

    else:

        st.warning(
            "Awaiting pipeline execution."
        )


with staging_col:

    st.markdown("### STAGING")

    st.caption(
        "Data transformation"
    )

    if pipeline_status == "SUCCESS":

        st.success(
            "STAGING transformation completed."
        )

    elif pipeline_status == "NO_NEW_RECORDS":

        st.info(
            "Skipped — no new records available."
        )

    else:

        st.warning(
            "Awaiting pipeline execution."
        )


with analytics_col:

    st.markdown("### ANALYTICS")

    st.caption(
        "Business-ready data"
    )

    if pipeline_status == "SUCCESS":

        st.success(
            "ANALYTICS transformation completed."
        )

    elif pipeline_status == "NO_NEW_RECORDS":

        st.info(
            "Skipped — no new records available."
        )

    else:

        st.warning(
            "Awaiting pipeline execution."
        )


# =====================================================
# DATA QUALITY MONITORING
# =====================================================

st.divider()

st.subheader("Data Quality Monitoring")

if result:

    previously_processed = result.get(
        "previously_processed_count"
    )

    batch_duplicates = result.get(
        "batch_duplicate_count"
    )

    validation_status = (
        "Passed"
        if result.get("status") in [
            "SUCCESS",
            "NO_NEW_RECORDS",
        ]
        else "Unknown"
    )

    quality_col1, quality_col2, quality_col3 = (
        st.columns(3)
    )

    with quality_col1:

        st.metric(
            "Previously Processed",
            (
                previously_processed
                if previously_processed is not None
                else "N/A"
            ),
        )

    with quality_col2:

        st.metric(
            "Batch Duplicates",
            (
                batch_duplicates
                if batch_duplicates is not None
                else "N/A"
            ),
        )

    with quality_col3:

        st.metric(
            "Validation Status",
            validation_status,
        )

else:

    quality_col1, quality_col2, quality_col3 = (
        st.columns(3)
    )

    with quality_col1:
        st.metric("Previously Processed", "—")

    with quality_col2:
        st.metric("Batch Duplicates", "—")

    with quality_col3:
        st.metric("Validation Status", "—")


# =====================================================
# PIPELINE RECOVERY
# =====================================================

st.divider()

st.subheader("Pipeline Recovery")

if result:

    recovered = result.get(
        "recovered_batch",
        False,
    )

    recovery_col1, recovery_col2 = st.columns(2)

    with recovery_col1:

        st.metric(
            "Pending Batch",
            (
                "Recovered"
                if recovered
                else "No recovery"
            ),
        )

    with recovery_col2:

        st.metric(
            "Recovery Status",
            (
                "Recovered successfully"
                if recovered
                else "Not required"
            ),
        )

else:

    recovery_col1, recovery_col2 = st.columns(2)

    with recovery_col1:
        st.metric("Pending Batch", "—")

    with recovery_col2:
        st.metric("Recovery Status", "Not executed")


# =====================================================
# BATCH INFORMATION
# =====================================================

if result:

    st.divider()

    st.subheader("Batch Information")

    batch_id = result.get(
        "batch_id"
    )

    st.write(
        "**Batch ID:**",
        batch_id if batch_id else "Not available",
    )

    if result.get("message"):

        st.caption(
            result["message"]
        )

    with st.expander(
        "View complete pipeline response"
    ):

        st.json(result)


# =====================================================
# PIPELINE EXECUTION HISTORY
# =====================================================

st.divider()

st.subheader("Pipeline Execution History")

history_col1, history_col2 = st.columns([3, 1])

with history_col1:

    st.caption(
        "Historical ELT executions retrieved from PostgreSQL."
    )

with history_col2:

    refresh_history = st.button(
        "🔄 Refresh History",
        use_container_width=True,
    )


if refresh_history:
    st.rerun()


history_data = fetch_pipeline_history(
    limit=20,
    offset=0,
)


if history_data:

    runs = history_data.get(
        "runs",
        [],
    )

    total_runs = history_data.get(
        "total",
        0,
    )

    st.metric(
        "Total Pipeline Executions",
        total_runs,
    )

    if runs:

        history_df = pd.DataFrame(runs)

        display_columns = [
            "id",
            "batch_id",
            "status",
            "extracted_records",
            "previously_processed",
            "batch_duplicates",
            "new_records",
            "loaded_records",
            "recovered_batch",
            "duration_seconds",
            "started_at",
            "completed_at",
        ]

        # Keep only columns returned by the API.
        available_columns = [
            column
            for column in display_columns
            if column in history_df.columns
        ]

        history_df = history_df[
            available_columns
        ]

        st.dataframe(
            history_df,
            use_container_width=True,
            hide_index=True,
        )

        # ---------------------------------------------
        # INDIVIDUAL EXECUTION DETAILS
        # ---------------------------------------------

        st.subheader("Execution Details")

        selected_run_id = st.selectbox(
            "Select Execution ID",
            options=[
                run["id"]
                for run in runs
            ],
        )

        selected_run = next(
            (
                run
                for run in runs
                if run["id"] == selected_run_id
            ),
            None,
        )

        if selected_run:

            with st.expander(
                f"Execution #{selected_run_id} Details",
                expanded=True,
            ):

                st.json(
                    selected_run
                )

        # ---------------------------------------------
        # DOWNLOAD HISTORY
        # ---------------------------------------------

        csv_data = history_df.to_csv(
            index=False
        ).encode("utf-8")

        st.download_button(
            label="📥 Download Execution History CSV",
            data=csv_data,
            file_name="elt_pipeline_history.csv",
            mime="text/csv",
        )

    else:

        st.info(
            "No pipeline executions found."
        )

else:

    st.warning(
        "Pipeline execution history is currently unavailable."
    )


# =====================================================
# FOOTER
# =====================================================

st.divider()

st.caption(
    "AI Task Management System | ELT Pipeline Monitoring"
)
