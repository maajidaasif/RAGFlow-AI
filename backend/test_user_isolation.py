"""
test_user_isolation.py
======================
Proves that User A cannot access, modify, delete, or
retrieve User B's papers and analysis history.

Run from the backend/ folder with venv active:
    python -m pytest test_user_isolation.py -v
"""

import pytest
import bcrypt
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from app import app, db
from models.user_model import User
from models.paper_model import Paper
from models.analysis_model import Analysis


# ============================================================
# FIXTURES
# ============================================================

def make_hashed(password: str) -> str:
    return bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")


@pytest.fixture
def client():
    """Isolated in-memory DB test client."""

    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["JWT_SECRET_KEY"] = "isolation-test-secret"

    with app.app_context():
        db.drop_all()
        db.create_all()

        # User A
        user_a = User(
            full_name="Alice",
            email="alice@example.com",
            password=make_hashed("alice_pass")
        )
        # User B
        user_b = User(
            full_name="Bob",
            email="bob@example.com",
            password=make_hashed("bob_pass")
        )
        db.session.add_all([user_a, user_b])
        db.session.commit()

        # Paper belonging to User A
        paper_a = Paper(
            user_id=user_a.id,
            filename="alice_paper.pdf",
            filepath="uploads/alice_paper.pdf"
        )
        # Paper belonging to User B
        paper_b = Paper(
            user_id=user_b.id,
            filename="bob_paper.pdf",
            filepath="uploads/bob_paper.pdf"
        )
        db.session.add_all([paper_a, paper_b])
        db.session.commit()

        # Analysis belonging to User A
        analysis_a = Analysis(
            user_id=user_a.id,
            analysis_type="Paper Comparison",
            analysis_name="Alice Analysis",
            domain="AI",
            papers="alice_paper.pdf",
            result="Alice result"
        )
        # Analysis belonging to User B
        analysis_b = Analysis(
            user_id=user_b.id,
            analysis_type="Literature Survey",
            analysis_name="Bob Analysis",
            domain="ML",
            papers="bob_paper.pdf",
            result="Bob result"
        )
        db.session.add_all([analysis_a, analysis_b])
        db.session.commit()

    with app.test_client() as c:
        yield c
    with app.app_context():
        db.drop_all()


def get_token(client, email, password):
    """Log in and return the JWT access token."""
    resp = client.post(
        "/login",
        json={"email": email, "password": password}
    )
    return resp.get_json()["access_token"]


def auth(token):
    return {"Authorization": f"Bearer {token}"}


# ============================================================
# PAPER ISOLATION
# ============================================================

class TestPaperIsolation:

    def test_user_a_sees_only_own_papers(self, client):
        """GET /papers returns only Alice's papers, not Bob's."""
        token = get_token(client, "alice@example.com", "alice_pass")
        resp = client.get("/papers", headers=auth(token))
        assert resp.status_code == 200
        papers = resp.get_json()
        filenames = [p["filename"] for p in papers]
        assert "alice_paper.pdf" in filenames
        assert "bob_paper.pdf" not in filenames

    def test_user_b_sees_only_own_papers(self, client):
        """GET /papers returns only Bob's papers, not Alice's."""
        token = get_token(client, "bob@example.com", "bob_pass")
        resp = client.get("/papers", headers=auth(token))
        assert resp.status_code == 200
        papers = resp.get_json()
        filenames = [p["filename"] for p in papers]
        assert "bob_paper.pdf" in filenames
        assert "alice_paper.pdf" not in filenames

    def test_user_a_cannot_delete_user_b_paper(self, client):
        """Alice must not be able to delete Bob's paper."""
        # Get Bob's paper ID first using Bob's token
        token_b = get_token(client, "bob@example.com", "bob_pass")
        papers_b = client.get(
            "/papers", headers=auth(token_b)
        ).get_json()
        bob_paper_id = papers_b[0]["id"]

        # Try to delete using Alice's token
        token_a = get_token(client, "alice@example.com", "alice_pass")
        resp = client.delete(
            f"/paper/{bob_paper_id}",
            headers=auth(token_a)
        )
        # Must be 404 — Alice has no paper with that ID
        assert resp.status_code == 404

    def test_user_b_cannot_delete_user_a_paper(self, client):
        """Bob must not be able to delete Alice's paper."""
        token_a = get_token(client, "alice@example.com", "alice_pass")
        papers_a = client.get(
            "/papers", headers=auth(token_a)
        ).get_json()
        alice_paper_id = papers_a[0]["id"]

        token_b = get_token(client, "bob@example.com", "bob_pass")
        resp = client.delete(
            f"/paper/{alice_paper_id}",
            headers=auth(token_b)
        )
        assert resp.status_code == 404

    def test_user_a_cannot_view_user_b_pdf(self, client):
        """Alice must get 404 when requesting Bob's PDF filename."""
        token_a = get_token(client, "alice@example.com", "alice_pass")
        resp = client.get(
            "/uploads/bob_paper.pdf",
            headers=auth(token_a)
        )
        assert resp.status_code == 404


# ============================================================
# ANALYSIS HISTORY ISOLATION
# ============================================================

class TestAnalysisIsolation:

    def test_user_a_sees_only_own_history(self, client):
        """GET /analysis-history returns only Alice's analyses."""
        token = get_token(client, "alice@example.com", "alice_pass")
        resp = client.get("/analysis-history", headers=auth(token))
        assert resp.status_code == 200
        history = resp.get_json()
        names = [a["analysis_name"] for a in history]
        assert "Alice Analysis" in names
        assert "Bob Analysis" not in names

    def test_user_b_sees_only_own_history(self, client):
        """GET /analysis-history returns only Bob's analyses."""
        token = get_token(client, "bob@example.com", "bob_pass")
        resp = client.get("/analysis-history", headers=auth(token))
        assert resp.status_code == 200
        history = resp.get_json()
        names = [a["analysis_name"] for a in history]
        assert "Bob Analysis" in names
        assert "Alice Analysis" not in names

    def test_user_a_cannot_delete_user_b_analysis(self, client):
        """Alice must not be able to delete Bob's analysis."""
        # Get Bob's analysis ID
        token_b = get_token(client, "bob@example.com", "bob_pass")
        history_b = client.get(
            "/analysis-history", headers=auth(token_b)
        ).get_json()
        bob_analysis_id = history_b[0]["id"]

        # Try delete with Alice's token
        token_a = get_token(client, "alice@example.com", "alice_pass")
        resp = client.delete(
            f"/analysis-history/{bob_analysis_id}",
            headers=auth(token_a)
        )
        assert resp.status_code == 404

    def test_user_b_cannot_delete_user_a_analysis(self, client):
        """Bob must not be able to delete Alice's analysis."""
        token_a = get_token(client, "alice@example.com", "alice_pass")
        history_a = client.get(
            "/analysis-history", headers=auth(token_a)
        ).get_json()
        alice_analysis_id = history_a[0]["id"]

        token_b = get_token(client, "bob@example.com", "bob_pass")
        resp = client.delete(
            f"/analysis-history/{alice_analysis_id}",
            headers=auth(token_b)
        )
        assert resp.status_code == 404


# ============================================================
# DASHBOARD ISOLATION
# ============================================================

class TestDashboardIsolation:

    def test_dashboard_counts_only_own_data(self, client):
        """Dashboard stats must reflect only the user's own records."""
        token_a = get_token(client, "alice@example.com", "alice_pass")
        resp = client.get("/dashboard", headers=auth(token_a))
        assert resp.status_code == 200
        data = resp.get_json()
        # Alice has 1 paper and 1 analysis
        assert data["total_papers"] == 1
        assert data["total_analysis"] == 1

        token_b = get_token(client, "bob@example.com", "bob_pass")
        resp_b = client.get("/dashboard", headers=auth(token_b))
        data_b = resp_b.get_json()
        # Bob has 1 paper and 1 analysis
        assert data_b["total_papers"] == 1
        assert data_b["total_analysis"] == 1
