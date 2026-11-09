
import uuid

from fastapi.testclient import TestClient
from sqlalchemy import delete

from fastapi_backend.main import app
from fastapi_backend.database import SessionLocal
from fastapi_backend.db_models import User

suffix = uuid.uuid4().hex[:12]

email_a = f"user_a_{suffix}@example.com"
email_b = f"user_b_{suffix}@example.com"
password = "TestPassword123!"

user_emails = [email_a, email_b]

try:
    with TestClient(app) as client:

        # 1. Register two users
        response_a = client.post(
            "/auth/register",
            json={"email": email_a, "password": password},
        )
        response_b = client.post(
            "/auth/register",
            json={"email": email_b, "password": password},
        )

        assert response_a.status_code == 201
        assert response_b.status_code == 201

        user_a_id = response_a.json()["user_id"]
        user_b_id = response_b.json()["user_id"]

        print("1. Two users registered: PASSED")

        # 2. Login both users
        login_a = client.post(
            "/auth/login",
            json={"email": email_a, "password": password},
        )
        login_b = client.post(
            "/auth/login",
            json={"email": email_b, "password": password},
        )

        assert login_a.status_code == 200
        assert login_b.status_code == 200

        token_a = login_a.json()["access_token"]
        token_b = login_b.json()["access_token"]

        headers_a = {"Authorization": f"Bearer {token_a}"}
        headers_b = {"Authorization": f"Bearer {token_b}"}

        print("2. Both users logged in: PASSED")

        # 3. Create a task for User A
        response = client.post(
            "/user-tasks/",
            json={"task_title": "Integration Test Task"},
            headers=headers_a,
        )

        assert response.status_code == 201

        task_id = response.json()["task_id"]

        assert response.json()["user_id"] == user_a_id

        print("3. Task creation: PASSED")

        # 4. Retrieve User A's task
        response = client.get(
            f"/user-tasks/{task_id}",
            headers=headers_a,
        )

        assert response.status_code == 200
        assert response.json()["task_title"] == "Integration Test Task"

        print("4. Task retrieval: PASSED")

        # 5. Update User A's task
        response = client.patch(
            f"/user-tasks/{task_id}",
            json={
                "task_title": "Updated Integration Test Task",
                "is_completed": True,
            },
            headers=headers_a,
        )

        assert response.status_code == 200
        assert response.json()["is_completed"] is True

        print("5. Task update: PASSED")

        # 6. Test pagination
        response = client.get(
            "/user-tasks/?page=1&page_size=1",
            headers=headers_a,
        )

        assert response.status_code == 200
        assert response.json()["page"] == 1
        assert response.json()["page_size"] == 1
        assert len(response.json()["data"]) <= 1

        print("6. Task pagination: PASSED")

        # 7. User B must not access User A's task
        response = client.get(
            f"/user-tasks/{task_id}",
            headers=headers_b,
        )
        assert response.status_code == 404

        response = client.patch(
            f"/user-tasks/{task_id}",
            json={"task_title": "Unauthorized update"},
            headers=headers_b,
        )
        assert response.status_code == 404

        response = client.delete(
            f"/user-tasks/{task_id}",
            headers=headers_b,
        )
        assert response.status_code == 404

        print("7. Cross-user access protection: PASSED")

        # 8. Reject unauthenticated task access
        response = client.get("/user-tasks/")

        assert response.status_code in (401, 403)

        print("8. Unauthenticated access rejection: PASSED")

        # 9. Delete User A's task
        response = client.delete(
            f"/user-tasks/{task_id}",
            headers=headers_a,
        )

        assert response.status_code == 204

        print("9. Task deletion: PASSED")

        # 10. Confirm task no longer exists
        response = client.get(
            f"/user-tasks/{task_id}",
            headers=headers_a,
        )

        assert response.status_code == 404

        print("10. Deleted task verification: PASSED")

        print("\nALL CRUD AND SECURITY TESTS PASSED")

finally:
    # Delete only the two uniquely generated test accounts.
    # Their tasks are removed through ON DELETE CASCADE.
    db = SessionLocal()

    try:
        db.execute(
            delete(User).where(User.email.in_(user_emails))
        )
        db.commit()

        print("Temporary test accounts cleaned up.")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()
