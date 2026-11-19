
import os
import uuid
from pathlib import Path

import pytest
from dotenv import load_dotenv
from fastapi.testclient import TestClient
from sqlalchemy import delete
from sqlalchemy.engine import URL

PROJECT_ROOT = Path(__file__).resolve().parents[1]
TEST_ENV_FILE = PROJECT_ROOT / ".env.test"

# Ensure the isolated test environment exists.
if not TEST_ENV_FILE.exists():
    raise RuntimeError(".env.test file is missing.")

load_dotenv(TEST_ENV_FILE, override=True)

test_db_password = os.getenv("TEST_DB_PASSWORD")

if not test_db_password:
    raise RuntimeError(
        "TEST_DB_PASSWORD is missing from .env.test."
    )

# Construct the isolated test database URL safely.
test_url = URL.create(
    drivername="postgresql+psycopg2",
    username="postgres",
    password=test_db_password,
    host="127.0.0.1",
    port=5432,
    database="ai_task_management_test",
)

# Verify the intended test database configuration.
if (
    test_url.database != "ai_task_management_test"
    or test_url.host != "127.0.0.1"
    or test_url.port != 5432
):
    raise RuntimeError(
        "Unsafe test database configuration."
    )

# Override DATABASE_URL before importing the application.
os.environ["DATABASE_URL"] = test_url.render_as_string(
    hide_password=False
)

# Import database and models before creating tables.
from fastapi_backend.database import Base, SessionLocal, engine
from fastapi_backend import db_models
from fastapi_backend.main import app

# Verify the actual application database connection.
actual_url = engine.url

if (
    actual_url.database != "ai_task_management_test"
    or actual_url.host != "127.0.0.1"
    or actual_url.port != 5432
):
    raise RuntimeError(
        "FastAPI is not connected to the isolated test database."
    )

# Create missing tables only in the isolated test database.
Base.metadata.create_all(bind=engine)


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def registered_user(client):
    suffix = uuid.uuid4().hex[:12]

    email = f"test_user_{suffix}@example.com"
    user_password = "TestPassword123!"

    response = client.post(
        "/auth/register",
        json={
            "email": email,
            "password": user_password,
        },
    )

    assert response.status_code == 201

    user_data = response.json()

    yield {
        "email": email,
        "password": user_password,
        "user_id": user_data["user_id"],
    }

    db = SessionLocal()

    try:
        db.execute(
            delete(db_models.User).where(
                db_models.User.email == email
            )
        )
        db.commit()

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()
