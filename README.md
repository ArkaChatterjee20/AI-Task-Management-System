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
- **Cloud Deployment:** Containerized frontend and backend deployed using AWS ECS Fargate.

## 🏗️ System Architecture

The application follows a modular architecture:

1. **Frontend:** Streamlit provides the user interface.
2. **Backend:** FastAPI handles API requests, ML operations, and pipeline functionality.
3. **Machine Learning:** Python-based ML components perform task prediction.
4. **Database:** PostgreSQL stores application data and prediction-related records.
5. **Data Engineering:** Python-based ELT workflows extract, transform, and load data into Snowflake.
6. **Containerization:** Docker packages the frontend and backend services.
7. **Cloud Infrastructure:** AWS ECS Fargate hosts the application, with an Application Load Balancer routing incoming requests.

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
| Containerization | Docker, Docker Compose |
| Cloud | AWS ECS Fargate, Amazon ECR, Application Load Balancer |
| Version Control | Git, GitHub |

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

```bash
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

## ☁️ AWS Deployment

The application is deployed using:

- **Amazon ECS Fargate:** Runs the frontend and backend containers.
- **Amazon ECR:** Stores Docker container images.
- **Application Load Balancer:** Routes incoming traffic to the appropriate ECS service.
- **CloudWatch Logs:** Supports container log monitoring.

The deployment architecture and sanitized ECS task definition examples are available in the repository.

## 📈 Scalability Considerations

The system design includes considerations for supporting approximately 150 concurrent users through resource allocation, service separation, and infrastructure scaling.

**Note:** This is a proposed capacity target, not a result of completed 150-user load testing.

## 🔐 Security

- Environment variables are used for configuration.
- Credentials and local deployment configurations are excluded from Git.
- Sanitized configuration templates are provided for reference.
- Production secrets should be managed securely and never committed to source control.

## 👨‍💻 Author

**Arka Chatterjee**

B.Tech in Information Technology | 2025

Interested in Data Engineering, Machine Learning, Python, SQL, and Cloud Technologies.

- GitHub: [ArkaChatterjee20](https://github.com/ArkaChatterjee20)

---
## Demo Link - http://ai-task-alb-45721397.ap-south-1.elb.amazonaws.com

If you find this project interesting, consider giving the repository a ⭐ on GitHub.

