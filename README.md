# AI Task Management System

An AI-powered task management platform combining machine learning, data engineering, and cloud deployment. The application provides a Streamlit interface, FastAPI backend, ML-powered task predictions, and an ELT pipeline integrated with cloud data services.

## 🚀 Live Application

**[Open AI Task Management System](http://ai-task-alb-45721397.ap-south-1.elb.amazonaws.com)**

The application is deployed on AWS ECS Fargate and accessed through an Application Load Balancer.

**[View Source Code on GitHub](https://github.com/ArkaChatterjee20/AI-Task-Management-System)**

## ✨ Key Features

- **Task Management:** Manage and organize tasks through an interactive Streamlit application.
- **Machine Learning:** Use a trained ML model to classify and predict task-related information.
- **ML Analytics:** View prediction analytics and model-related insights.
- **Prediction History:** Access previously generated ML predictions.
- **ELT Pipeline:** Extract data from APIs, process records, handle duplicates, and load data into the target data platform.
- **Pipeline Monitoring:** Track extraction and loading runs, processing status, and pipeline execution history.
- **REST API:** FastAPI backend providing application and ML pipeline endpoints.
- **Database Integration:** PostgreSQL for application data and Snowflake for data engineering workflows.
- **Workflow Orchestration:** Apache Airflow orchestrates ELT pipeline execution and end-to-end integration testing.
- **Cloud Deployment:** Containerized frontend and backend deployed using AWS ECS Fargate.

## 🏗️ System Architecture

The application follows a modular architecture:

1. **Frontend:** Streamlit provides the user interface.
2. **Backend:** FastAPI handles API requests, ML operations, and pipeline functionality.
3. **Machine Learning:** Python-based ML components perform task prediction.
4. **Database:** PostgreSQL stores application data and prediction-related records.
5. **Data Engineering:** Python-based ELT workflows extract, transform, and load data into Snowflake.
6. **Workflow Orchestration:** Apache Airflow manages ELT execution and integration testing.
7. **Containerization:** Docker packages the frontend, backend, and local Airflow services.
8. **Cloud Infrastructure:** AWS ECS Fargate hosts the application, with an Application Load Balancer routing incoming requests.

## 🛠️ Technology Stack

| Category | Technologies |
|---|---|
| Programming | Python, SQL |
| Frontend | Streamlit |
| Backend | FastAPI |
| Machine Learning | Scikit-learn, Pandas, NumPy |
| Database | PostgreSQL |
| Data Warehouse | Snowflake |
| Data Engineering | Python, REST APIs, ELT |
| Workflow Orchestration | Apache Airflow 3.4.0 |
| Containerization | Docker, Docker Compose |
| Cloud | AWS ECS Fargate, Amazon ECR, Application Load Balancer |
| Version Control | Git, GitHub |
| CI | GitHub Actions |

## 📂 Project Documentation

Detailed technical documentation is available in the `docs/` directory.

| Document | Description |
|---|---|
| [System Architecture](docs/system-architecture.md) | Overall system architecture and component interactions |
| [Low-Level System Design](docs/low-level-system-design.md) | Component-level design and proposed scalability considerations |
| [ELT Pipeline Architecture](docs/elt-pipeline-architecture.md) | Data extraction, transformation, loading, and tracking |
| [Data Architecture](docs/data-architecture.md) | Database and data flow design |
| [Deployment Architecture](docs/deployment-architecture.md) | Docker and AWS deployment architecture |

## ⚙️ Run Locally Using Docker

### Prerequisites

- Python 3.11
- Docker Desktop
- Docker Compose
- PostgreSQL
- Required Snowflake credentials for data warehouse functionality

### 1. Clone the repository

```bash
git clone https://github.com/ArkaChatterjee20/AI-Task-Management-System.git
cd AI-Task-Management-System
```

### 2. Configure environment variables

Create your local `.env` file using the example:

```powershell
copy .env.example .env
```

Update the environment variables with your own PostgreSQL, Snowflake, and application configuration.

**Never commit your actual `.env` file or credentials to GitHub.**

### 3. Build and start the application

```bash
docker compose build
docker compose up -d
```

### 4. Access the application

| Service | Local URL |
|---|---|
| Streamlit Frontend | http://localhost:8501 |
| FastAPI Backend | http://localhost:8001 |
| FastAPI Swagger Documentation | http://localhost:8001/docs |
| Backend Health Check | http://localhost:8001/health |

To stop the application:

```bash
docker compose down
```

## 🔄 Local Apache Airflow Deployment

Apache Airflow is used locally to orchestrate the ELT pipeline and execute end-to-end Snowflake integration tests.

The Airflow environment runs separately from the existing AWS application deployment using Docker Compose.

### Airflow Architecture

- **Airflow API Server:** Provides the Airflow web interface.
- **Airflow Scheduler:** Schedules and executes DAG tasks.
- **DAG Processor:** Parses and processes DAG definitions.
- **Airflow Metadata Database:** PostgreSQL stores Airflow metadata and execution information.
- **Snowflake:** Stores raw, staging, and analytics data for ELT processing.

### 1. Configure Airflow environment

Create your local Airflow environment file:

```powershell
copy .env.airflow.example .env.airflow
```

Update `.env.airflow` with your own values, including:

- Airflow PostgreSQL credentials.
- Airflow Fernet and API security keys.
- Snowflake account and authentication credentials.
- Snowflake warehouse and database configuration.

The example configuration uses isolated Snowflake schemas:

- `AIRFLOW_TEST_RAW`
- `AIRFLOW_TEST_STAGING`
- `AIRFLOW_TEST_ANALYTICS`

Use your own credentials and never commit `.env.airflow` to GitHub.

### 2. Build and start Airflow

```powershell
docker compose --env-file .env.airflow -f docker-compose.airflow.yml build
```

Start the Airflow services:

```powershell
docker compose --env-file .env.airflow -f docker-compose.airflow.yml up -d
```

### 3. Access the Airflow UI

Open the following address in your browser:

**http://localhost:8080**

This is a local-only address. It is accessible from the machine running Docker and is not a publicly hosted Airflow URL.

### 4. Available Airflow DAGs

| DAG | Responsibility |
|---|---|
| `ai_task_management_elt_dag` | Orchestrates the existing ELT pipeline. |
| `ai_task_management_e2e_test_dag` | Executes isolated end-to-end Snowflake integration testing. |

**Main ELT DAG:**

- Executes the existing API-based ELT pipeline.
- Handles extraction and loading.
- Uses configurable local ELT storage.
- Supports retries and execution monitoring.

**End-to-End Integration Test DAG:**

- Loads a synthetic test record into an isolated Snowflake raw schema.
- Executes staging transformations.
- Executes analytics transformations.
- Validates the expected analytics result.

### 5. Monitor Airflow services

Check the Airflow containers:

```powershell
docker ps -a --filter "name=ai-task-airflow"
```

View scheduler logs:

```powershell
docker logs ai-task-airflow-scheduler
```

### 6. Stop Airflow

```powershell
docker compose --env-file .env.airflow -f docker-compose.airflow.yml down
```

This stops the local Airflow services without changing the existing AWS application deployment. Persistent Airflow metadata is retained unless its Docker volume is explicitly removed.
## Apache Airflow UI Demo

The AI Task Management ELT pipeline is orchestrated using Apache Airflow 3.4.0.

**Live Demo:** [Open Airflow Dashboard](https://massachusetts-xml-independence-thu.trycloudflare.com)

### Available DAGs
- `ai_task_management_elt_dag`
- `ai_task_management_e2e_test_dag`

**Note:** This is a temporary Cloudflare Quick Tunnel connected to a locally hosted Airflow instance. Availability depends on the local machine, Docker containers, and tunnel process being active. The URL may change when the tunnel restarts.

## ☁️ AWS Deployment

The application is deployed using:

- **Amazon ECS Fargate:** Runs the frontend and backend containers.
- **Amazon ECR:** Stores Docker container images.
- **Application Load Balancer:** Routes incoming traffic to the appropriate ECS service.
- **CloudWatch Logs:** Supports container log monitoring.

The deployment architecture and sanitized ECS task definition examples are available in the repository.

Apache Airflow currently runs locally through Docker Compose and is separate from the AWS-hosted application.

## 📈 Scalability Considerations

The system design includes considerations for supporting approximately 150 concurrent users through resource allocation, service separation, and infrastructure scaling.

**Note:** This is a proposed capacity target, not a result of completed 150-user load testing.

## 🔐 Security

- Environment variables are used for configuration.
- Credentials and local deployment configurations are excluded from Git.
- Sanitized configuration templates are provided for reference.
- Production secrets should be managed securely and never committed to source control.
- Airflow is bound to localhost for local development rather than exposed publicly.

## 👨‍💻 Author

**Arka Chatterjee**

B.Tech in Information Technology | 2025

Interested in Data Engineering, Machine Learning, Python, SQL, and Cloud Technologies.

- GitHub: [ArkaChatterjee20](https://github.com/ArkaChatterjee20)

---

## Demo Link

http://ai-task-alb-45721397.ap-south-1.elb.amazonaws.com

If you find this project interesting, consider giving the repository a ⭐ on GitHub.
