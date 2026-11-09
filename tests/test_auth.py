def test_user_registration(client, registered_user):
    assert registered_user["user_id"] > 0


def test_duplicate_registration(client, registered_user):
    response = client.post(
        "/auth/register",
        json={
            "email": registered_user["email"],
            "password": registered_user["password"],
        },
    )

    assert response.status_code == 409


def test_user_login(client, registered_user):
    response = client.post(
        "/auth/login",
        json={
            "email": registered_user["email"],
            "password": registered_user["password"],
        },
    )

    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"


def test_login_with_wrong_password(client, registered_user):
    response = client.post(
        "/auth/login",
        json={
            "email": registered_user["email"],
            "password": "WrongPassword123!",
        },
    )

    assert response.status_code == 401


def test_authenticated_user_profile(client, registered_user):
    login_response = client.post(
        "/auth/login",
        json={
            "email": registered_user["email"],
            "password": registered_user["password"],
        },
    )

    token = login_response.json()["access_token"]

    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json()["email"] == registered_user["email"]


def test_invalid_token_rejected(client):
    response = client.get(
        "/auth/me",
        headers={"Authorization": "Bearer invalid-token"},
    )

    assert response.status_code == 401