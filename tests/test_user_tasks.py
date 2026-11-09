import uuid

from sqlalchemy import delete

from fastapi_backend.database import SessionLocal
from fastapi_backend.db_models import User


def get_auth_headers(client, user):
    response = client.post(
        "/auth/login",
        json={
            "email": user["email"],
            "password": user["password"],
        },
    )

    assert response.status_code == 200

    token = response.json()["access_token"]

    return {"Authorization": f"Bearer {token}"}


def test_create_task(client, registered_user):
    headers = get_auth_headers(client, registered_user)

    response = client.post(
        "/user-tasks/",
        json={"task_title": "Learn FastAPI"},
        headers=headers,
    )

    assert response.status_code == 201
    assert response.json()["task_title"] == "Learn FastAPI"
    assert response.json()["user_id"] == registered_user["user_id"]


def test_list_user_tasks(client, registered_user):
    headers = get_auth_headers(client, registered_user)

    client.post(
        "/user-tasks/",
        json={"task_title": "Task One"},
        headers=headers,
    )

    response = client.get(
        "/user-tasks/",
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["total_tasks"] >= 1


def test_task_pagination(client, registered_user):
    headers = get_auth_headers(client, registered_user)

    for number in range(3):
        client.post(
            "/user-tasks/",
            json={"task_title": f"Pagination Task {number}"},
            headers=headers,
        )

    response = client.get(
        "/user-tasks/?page=1&page_size=2",
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["page_size"] == 2
    assert len(response.json()["data"]) <= 2


def test_update_task(client, registered_user):
    headers = get_auth_headers(client, registered_user)

    created = client.post(
        "/user-tasks/",
        json={"task_title": "Original Task"},
        headers=headers,
    )

    task_id = created.json()["task_id"]

    response = client.patch(
        f"/user-tasks/{task_id}",
        json={
            "task_title": "Updated Task",
            "is_completed": True,
        },
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["task_title"] == "Updated Task"
    assert response.json()["is_completed"] is True


def test_delete_task(client, registered_user):
    headers = get_auth_headers(client, registered_user)

    created = client.post(
        "/user-tasks/",
        json={"task_title": "Task To Delete"},
        headers=headers,
    )

    task_id = created.json()["task_id"]

    response = client.delete(
        f"/user-tasks/{task_id}",
        headers=headers,
    )

    assert response.status_code == 204

    response = client.get(
        f"/user-tasks/{task_id}",
        headers=headers,
    )

    assert response.status_code == 404


def test_user_cannot_access_another_users_task(
    client,
    registered_user,
):
    headers_a = get_auth_headers(client, registered_user)

    suffix = uuid.uuid4().hex[:12]
    email_b = f"second_user_{suffix}@example.com"
    password_b = "TestPassword123!"

    db = SessionLocal()

    try:
        # Register a second temporary user.
        registration = client.post(
            "/auth/register",
            json={
                "email": email_b,
                "password": password_b,
            },
        )

        assert registration.status_code == 201

        login_b = client.post(
            "/auth/login",
            json={
                "email": email_b,
                "password": password_b,
            },
        )

        assert login_b.status_code == 200

        headers_b = {
            "Authorization": (
                f"Bearer {login_b.json()['access_token']}"
            )
        }

        # User A creates a task.
        created = client.post(
            "/user-tasks/",
            json={"task_title": "Private Task"},
            headers=headers_a,
        )

        task_id = created.json()["task_id"]

        # User B must not access User A's task.
        response = client.get(
            f"/user-tasks/{task_id}",
            headers=headers_b,
        )

        assert response.status_code == 404

        response = client.patch(
            f"/user-tasks/{task_id}",
            json={"task_title": "Unauthorized Update"},
            headers=headers_b,
        )

        assert response.status_code == 404

        response = client.delete(
            f"/user-tasks/{task_id}",
            headers=headers_b,
        )

        assert response.status_code == 404

    finally:
        db.execute(
            delete(User).where(User.email == email_b)
        )
        db.commit()
        db.close()


def test_unauthenticated_user_cannot_access_tasks(client):
    response = client.get("/user-tasks/")

    assert response.status_code in (401, 403)