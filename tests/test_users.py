import os
import pytest

@pytest.fixture()
def test_app(tmp_path, monkeypatch):
    # Use a fresh SQLite file per test function
    dbfile = tmp_path / "test.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{dbfile}")
    # Optional: set predictable JWT values in tests
    monkeypatch.setenv("JWT_SECRET", "testsecret")
    monkeypatch.setenv("JWT_EXPIRE_MINUTES", "60")

    from app import create_app  # import after env vars are set
    app = create_app()
    return app

@pytest.fixture()
def client(test_app):
    return test_app.test_client()

def test_health(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.get_json()["status"] == "ok"

def test_user_crud_flow_with_auth(client):
    # Create (public)
    payload = {"email": "a@test.com", "password": "supersecret", "full_name": "Alpha Test"}
    res = client.post("/api/v1/users", json=payload)
    assert res.status_code == 201
    user_id = res.get_json()["id"]

    # Login → JWT
    res_login = client.post("/auth/login", json={"email": "a@test.com", "password": "supersecret"})
    assert res_login.status_code == 200
    token = res_login.get_json()["access_token"]
    auth_hdr = {"Authorization": f"Bearer {token}"}

    # Read (public)
    assert client.get(f"/api/v1/users/{user_id}").status_code == 200

    # List (public, paginated)
    assert client.get("/api/v1/users?limit=10&offset=0").status_code == 200

    # Update (protected)
    res_upd = client.patch(f"/api/v1/users/{user_id}", json={"full_name": "Alpha Updated"}, headers=auth_hdr)
    assert res_upd.status_code == 200
    assert res_upd.get_json()["full_name"] == "Alpha Updated"

    # Delete (protected)
    assert client.delete(f"/api/v1/users/{user_id}", headers=auth_hdr).status_code == 200

    # Not found after delete
    assert client.get(f"/api/v1/users/{user_id}").status_code == 404
