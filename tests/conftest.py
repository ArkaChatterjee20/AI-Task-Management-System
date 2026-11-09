import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import delete

from fastapi_backend.main import app
from fastapi_backend.database import SessionLocal
from fastapi_backend.db_models import User


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def registered_user(client):
    suffix = uuid.uuid4().hex[:12]

    email = f"test_user_{suffix}@example.com"
    password = "TestPassword123!"

    response = client.post(
        "/auth/register",
        json={
            "email": email,
            "password": password,
        },
    )

    assert response.status_code == 201

    user_data = response.json()

    yield {
        "email": email,
        "password": password,
        "user_id": user_data["user_id"],
    }

    db = SessionLocal()

    try:
        db.execute(
            delete(User).where(User.email == email)
        )
        db.commit()

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()