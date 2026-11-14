
import os
import requests
import streamlit as st

# ---------------- CONFIGURATION ----------------

API_BASE_URL = os.getenv(
    "API_BASE_URL",
    "http://api:8000"
).rstrip("/")

# ---------------- PAGE CONFIG ----------------

st.set_page_config(
    page_title="AI Task Manager",
    page_icon="🚀",
    layout="wide"
)

# ---------------- CUSTOM CSS ----------------

st.markdown("""
<style>
body {
    background-color: #0f172a;
}
.main {
    background-color: #0f172a;
}
.card {
    background-color: #1e293b;
    padding: 20px;
    border-radius: 12px;
    text-align: center;
    box-shadow: 0px 4px 10px rgba(0,0,0,0.4);
}
.metric {
    font-size: 22px;
    font-weight: bold;
}
.big-title {
    font-size: 40px;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------

st.markdown(
    '<div class="big-title">🚀 AI Task Management System</div>',
    unsafe_allow_html=True
)

st.write(
    "Automate task classification, prioritization, and assignment"
)

# ---------------- SESSION TEAM ----------------

if "team" not in st.session_state:
    st.session_state.team = {
        "Alice": 4,
        "Bob": 3,
        "Charlie": 2
    }


def assign_task():
    team = st.session_state.team

    person = min(team, key=team.get)

    team[person] += 1

    return person


# ---------------- SIDEBAR ----------------

st.sidebar.title("⚙️ Team Settings")

for member in st.session_state.team:
    st.session_state.team[member] = st.sidebar.slider(
        f"{member} workload",
        0,
        10,
        st.session_state.team[member]
    )


# ---------------- INPUT SECTION ----------------

st.markdown("### 📌 Enter Task Details")

col1, col2 = st.columns([2, 1])

with col1:
    task = st.text_area(
        "📝 Task Description",
        placeholder="e.g. Complete machine learning project"
    )

with col2:
    deadline = st.slider(
        "⏳ Deadline (days)",
        1,
        10,
        3
    )


# ---------------- PREDICTION ----------------

if st.button("🔍 Analyze Task", use_container_width=True):

    if not task.strip():

        st.warning("⚠️ Please enter a task description.")

    else:

        try:
            with st.spinner("Connecting to ML prediction API..."):

                response = requests.post(
                    f"{API_BASE_URL}/ml/predict-task",
                    json={
                        "task_title": task.strip()
                    },
                    timeout=30
                )

                response.raise_for_status()

                result = response.json()["prediction"]

                predicted_status = result["predicted_status"]
                prediction_value = result["prediction"]

            # -------- CATEGORY LOGIC --------

            task_lower = task.lower()

            if "gym" in task_lower or "exercise" in task_lower:
                category = "Health & Wellness"

            elif "flight" in task_lower or "travel" in task_lower:
                category = "Travel"

            elif "bill" in task_lower or "pay" in task_lower:
                category = "Finance"

            else:
                category = "Personal"

            # -------- PRIORITY LOGIC --------

            if deadline <= 2:
                priority = "High"

            elif deadline <= 5:
                priority = "Medium"

            else:
                priority = "Low"

            # -------- TEAM ASSIGNMENT --------

            assigned = assign_task()

            # -------- DISPLAY RESULTS --------

            st.success("✅ Task analyzed successfully using FastAPI!")

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric(
                    "Category",
                    category
                )

            with col2:
                st.metric(
                    "ML Predicted Status",
                    predicted_status
                )

            with col3:
                st.metric(
                    "Priority",
                    priority
                )

            with col4:
                st.metric(
                    "Assigned To",
                    assigned
                )

            st.caption(
                f"SVM prediction value: {prediction_value}"
            )

        except requests.exceptions.Timeout:

            st.error(
                "The prediction API timed out. Please try again."
            )

        except requests.exceptions.ConnectionError:

            st.error(
                "Cannot connect to FastAPI. "
                "Please check whether the API container is running."
            )

        except requests.exceptions.HTTPError as error:

            st.error(
                f"Prediction API returned an HTTP error: {error}"
            )

        except (KeyError, ValueError):

            st.error(
                "The prediction API returned an unexpected response."
            )

        except requests.exceptions.RequestException as error:

            st.error(
                f"API request failed: {error}"
            )


# ---------------- TEAM WORKLOAD ----------------

st.markdown("### 📊 Team Workload")

for member, tasks in st.session_state.team.items():

    st.progress(tasks / 10)

    st.write(f"{member}: {tasks} tasks")


# ---------------- FOOTER ----------------

st.markdown("---")

st.markdown(
    "💡 Built with Streamlit, FastAPI and Machine Learning"
)
