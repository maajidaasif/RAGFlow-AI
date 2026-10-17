import pytest

from app import app, db
from models.user_model import User


@pytest.fixture
def auth_client():
    app.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI="sqlite:///:memory:",
    )
    with app.app_context():
        db.drop_all()
        db.create_all()
        db.session.add(User(
            full_name="Auth Test",
            email="auth-test@example.com",
            password="unused",
        ))
        db.session.commit()
    with app.test_client() as client:
        yield client
    with app.app_context():
        db.drop_all()


@pytest.mark.parametrize("payload", [None, [], {"email": "bad"}])
def test_login_rejects_malformed_or_missing_fields(auth_client, payload):
    if payload is None:
        response = auth_client.post("/login", data="{", content_type="application/json")
    else:
        response = auth_client.post("/login", json=payload)

    assert response.status_code == 400
    assert response.is_json


@pytest.mark.parametrize("email", ["not-an-email", "x@", "@example.com"])
def test_register_rejects_invalid_email(auth_client, email):
    response = auth_client.post("/register", json={
        "full_name": "Test User",
        "email": email,
        "password": "secure-pass-123",
    })

    assert response.status_code == 400
    assert response.is_json