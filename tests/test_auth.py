def test_register_new_user(client):
    res = client.post("/api/auth/register", json={
        "name": "David Clark",
        "email": "david.clark@university.edu",
        "password": "SecurePassword123!"
    })
    assert res.status_code == 201
    data = res.json()
    assert "access_token" in data
    assert data["user"]["email"] == "david.clark@university.edu"
    assert data["user"]["name"] == "David Clark"


def test_register_duplicate_email_fails(client):
    # First registration
    client.post("/api/auth/register", json={
        "name": "First User",
        "email": "duplicate@test.com",
        "password": "Password123!"
    })

    # Second registration with identical email
    res = client.post("/api/auth/register", json={
        "name": "Second User",
        "email": "duplicate@test.com",
        "password": "DifferentPassword123!"
    })
    assert res.status_code == 400
    assert "already exists" in res.json()["detail"].lower()


def test_login_successful(client):
    client.post("/api/auth/register", json={
        "name": "Login User",
        "email": "login@test.com",
        "password": "Password123!"
    })

    res = client.post("/api/auth/login", json={
        "email": "login@test.com",
        "password": "Password123!"
    })
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["user"]["email"] == "login@test.com"


def test_login_invalid_password_fails(client):
    res = client.post("/api/auth/login", json={
        "email": "login@test.com",
        "password": "WrongPassword!"
    })
    assert res.status_code == 401
    assert "invalid" in res.json()["detail"].lower()


def test_get_current_user_profile(client, user1_auth):
    res = client.get("/api/auth/me", headers=user1_auth["headers"])
    assert res.status_code == 200
    data = res.json()
    assert data["email"] == user1_auth["user"]["email"]


def test_unauthorized_access_fails(client):
    # Missing authorization header
    res = client.get("/api/auth/me")
    assert res.status_code == 401

    # Invalid authorization token
    res = client.get("/api/auth/me", headers={"Authorization": "Bearer invalid_token_xyz"})
    assert res.status_code == 401
