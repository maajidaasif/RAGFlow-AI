"""
JWT Authentication Tests
========================
Tests that protected routes reject missing / invalid tokens
and accept valid tokens.

Run from the backend/ folder with venv active:
    python -m pytest test_jwt_auth.py -v
"""

import pytest
import json
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from app import app, db
from models.user_model import User
import bcrypt


# ============================================================
# FIXTURES
# ============================================================

@pytest.fixture
def client():
    """Create a test Flask client with an isolated in-memory DB."""

    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["JWT_SECRET_KEY"] = "test-jwt-secret"

    with app.app_context():
        db.drop_all()
        db.create_all()

        # Create a test user
        hashed = bcrypt.hashpw(
            b"testpassword123",
            bcrypt.gensalt()
        ).decode("utf-8")

        user = User(
            full_name="Test User",
            email="test@example.com",
            password=hashed
        )
        db.session.add(user)
        db.session.commit()

    with app.test_client() as client:
        yield client
    with app.app_context():
        db.drop_all()


@pytest.fixture
def valid_token(client):
    """Obtain a real JWT by logging in with the test user."""

    response = client.post(
        "/login",
        json={
            "email": "test@example.com",
            "password": "testpassword123"
        }
    )
    data = response.get_json()
    return data["access_token"]


# ============================================================
# HELPER
# ============================================================

def auth_header(token):
    return {"Authorization": f"Bearer {token}"}


# ============================================================
# PUBLIC ROUTES — must NOT require a token
# ============================================================

class TestPublicRoutes:

    def test_register_is_public(self, client):
        """POST /register should be accessible without a token."""
        response = client.post(
            "/register",
            json={
                "full_name": "New User",
                "email": "new@example.com",
                "password": "newpass123"
            }
        )
        # 201 created or 409 conflict — either way, not 401/422
        assert response.status_code not in (401, 422), (
            f"/register returned {response.status_code} — "
            "it should be public"
        )

    def test_login_is_public(self, client):
        """POST /login should be accessible without a token."""
        response = client.post(
            "/login",
            json={
                "email": "test@example.com",
                "password": "testpassword123"
            }
        )
        assert response.status_code == 200
        assert "access_token" in response.get_json()

    def test_home_is_public(self, client):
        """GET / health endpoint should be accessible without a token."""
        response = client.get("/")
        assert response.status_code == 200

    def test_system_status_is_public(self, client):
        """GET /system-status should be accessible without a token."""
        response = client.get("/system-status")
        assert response.status_code == 200


# ============================================================
# PROTECTED ROUTES — must REJECT missing token (401/422)
# ============================================================

PROTECTED_ROUTES = [
    # (method, path)
    ("GET",    "/profile"),
    ("GET",    "/papers"),
    ("POST",   "/upload-paper"),
    ("DELETE", "/paper/1"),
    ("GET",    "/compare-papers"),
    ("GET",    "/research-gap"),
    ("GET",    "/literature-survey"),
    ("GET",    "/analysis-history"),
    ("DELETE", "/analysis-history/1"),
    ("GET",    "/dashboard"),
    ("POST",   "/generate-report"),
    ("POST",   "/api/chat"),
]


class TestProtectedRoutesRejectNoToken:

    @pytest.mark.parametrize("method,path", PROTECTED_ROUTES)
    def test_rejects_missing_token(self, client, method, path):
        """Each protected route must return 401 or 422 without a token."""
        response = getattr(client, method.lower())(path)
        assert response.status_code in (401, 422), (
            f"{method} {path} returned {response.status_code} "
            f"with no token — expected 401 or 422"
        )

    @pytest.mark.parametrize("method,path", PROTECTED_ROUTES)
    def test_rejects_invalid_token(self, client, method, path):
        """Each protected route must return 401 or 422 with a bogus token."""
        response = getattr(client, method.lower())(
            path,
            headers={"Authorization": "Bearer this.is.not.a.valid.token"}
        )
        assert response.status_code in (401, 422), (
            f"{method} {path} returned {response.status_code} "
            f"with an invalid token — expected 401 or 422"
        )

    @pytest.mark.parametrize("method,path", PROTECTED_ROUTES)
    def test_rejects_malformed_header(self, client, method, path):
        """Malformed Authorization header must not bypass protection."""
        response = getattr(client, method.lower())(
            path,
            headers={"Authorization": "NotBearer sometoken"}
        )
        assert response.status_code in (401, 422), (
            f"{method} {path} returned {response.status_code} "
            f"with malformed header — expected 401 or 422"
        )


# ============================================================
# PROTECTED ROUTES — must ACCEPT a valid token (not 401/422)
# ============================================================

class TestProtectedRoutesAcceptValidToken:

    def test_profile_accepts_valid_token(self, client, valid_token):
        """GET /profile must return 200 with a valid token."""
        response = client.get(
            "/profile",
            headers=auth_header(valid_token)
        )
        assert response.status_code == 200
        data = response.get_json()
        assert "user" in data

    def test_papers_accepts_valid_token(self, client, valid_token):
        """GET /papers must not return 401/422 with a valid token."""
        response = client.get(
            "/papers",
            headers=auth_header(valid_token)
        )
        assert response.status_code not in (401, 422), (
            f"GET /papers returned {response.status_code} "
            f"with a valid token"
        )

    def test_analysis_history_accepts_valid_token(self, client, valid_token):
        """GET /analysis-history must not return 401/422 with a valid token."""
        response = client.get(
            "/analysis-history",
            headers=auth_header(valid_token)
        )
        assert response.status_code not in (401, 422), (
            f"GET /analysis-history returned {response.status_code} "
            f"with a valid token"
        )

    def test_dashboard_accepts_valid_token(self, client, valid_token):
        """GET /dashboard must not return 401/422 with a valid token."""
        response = client.get(
            "/dashboard",
            headers=auth_header(valid_token)
        )
        assert response.status_code not in (401, 422), (
            f"GET /dashboard returned {response.status_code} "
            f"with a valid token"
        )

    def test_chat_accepts_valid_token(self, client, valid_token):
        """POST /api/chat must not return 401/422 with a valid token."""
        response = client.post(
            "/api/chat",
            headers=auth_header(valid_token),
            json={"question": "hello"}
        )
        assert response.status_code not in (401, 422), (
            f"POST /api/chat returned {response.status_code} "
            f"with a valid token"
        )

    def test_compare_rejects_more_than_five_papers(self, client, valid_token):
        response = client.get(
            "/compare-papers?limit=6",
            headers=auth_header(valid_token),
        )

        assert response.status_code == 400
        assert response.get_json()["success"] is False
