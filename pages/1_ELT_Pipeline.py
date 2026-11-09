
import streamlit as st

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="ELT Pipeline Dashboard",
    page_icon="📊",
    layout="wide",
)

# ---------------- CUSTOM CSS ----------------

st.markdown(
    """
    <style>
    /* Main application background */
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

    /* Main content */
    .main .block-container {
        color: #f8fafc;
        padding-top: 2rem;
    }

    /* Dashboard header */
    .dashboard-header {
        font-size: 34px;
        font-weight: bold;
        color: #f8fafc;
    }

    .dashboard-subtitle {
        color: #94a3b8;
        font-size: 15px;
    }

    /* Section headings */
    h1, h2, h3, h4 {
        color: #f8fafc !important;
    }

    /* Metric cards */
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

    /* General text */
    .stMarkdown p,
    .stCaption {
        color: #cbd5e1;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ---------------- PIPELINE STATUS ----------------
st.subheader("Pipeline Overview")

col1, col2 = st.columns([2, 1])

with col1:
    st.info(
        "Live pipeline monitoring is not connected yet. "
        "The dashboard will display actual execution data after "
        "FastAPI job tracking is implemented."
    )

with col2:
    st.metric("Pipeline Status", "Not connected")

# ---------------- EXECUTION METRICS ----------------
st.subheader("Execution Metrics")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Extracted Records", "—")

with col2:
    st.metric("New Records", "—")

with col3:
    st.metric("Duplicate Records", "—")

with col4:
    st.metric("Loaded Records", "—")

st.divider()

# ---------------- DATA WAREHOUSE ----------------
st.subheader("Snowflake Data Warehouse")

raw_col, staging_col, analytics_col = st.columns(3)

with raw_col:
    st.markdown("### RAW")
    st.caption("Source data ingestion")
    st.warning("Awaiting live connection")

with staging_col:
    st.markdown("### STAGING")
    st.caption("Data transformation")
    st.warning("Awaiting live connection")

with analytics_col:
    st.markdown("### ANALYTICS")
    st.caption("Business-ready data")
    st.warning("Awaiting live connection")

st.divider()

# ---------------- DATA QUALITY ----------------
st.subheader("Data Quality Monitoring")

quality_col1, quality_col2, quality_col3 = st.columns(3)

with quality_col1:
    st.metric("Previously Processed", "—")

with quality_col2:
    st.metric("Batch Duplicates", "—")

with quality_col3:
    st.metric("Validation Status", "—")

st.divider()

# ---------------- RECOVERY MONITORING ----------------
st.subheader("Pipeline Recovery")

recovery_col1, recovery_col2 = st.columns(2)

with recovery_col1:
    st.metric("Pending Batch", "—")

with recovery_col2:
    st.metric("Recovery Status", "Not connected")

st.divider()

# ---------------- EXECUTION HISTORY ----------------
st.subheader("Pipeline Execution History")

st.info(
    "Execution history will appear here after durable "
    "pipeline run tracking is integrated with FastAPI."
)

# ---------------- FOOTER ----------------
st.divider()

st.caption(
    "AI Task Management System | ELT Pipeline Monitoring"
)
