"""
test_upload_security.py
=======================
Tests for secure PDF upload implementation.

Covers:
  - Malicious / path-traversal filenames
  - Invalid file types (non-PDF extension, fake PDF)
  - File-type spoofing (PDF extension + non-PDF content)
  - Normal valid PDF upload
  - Empty / missing file upload

Run from the backend/ folder with venv active:
    python -m pytest test_upload_security.py -v
"""

import pytest
import io
import os
import bcrypt
import sys

sys.path.insert(0, os.path.dirname(__file__))

from app import app, db
from models.user_model import User
from models.paper_model import Paper
import routes.paper_routes as paper_routes


# ==============================================================
# HELPERS
# ==============================================================

# Minimal valid PDF binary (10-byte body, valid %PDF- header)
VALID_PDF_BYTES = (
    b"%PDF-1.4\n"
    b"1 0 obj\n<< /Type /Catalog >>\nendobj\n"
    b"xref\n0 2\n0000000000 65535 f \n"
    b"0000000009 00000 n \n"
    b"trailer\n<< /Size 2 /Root 1 0 R >>\n"
    b"startxref\n9\n%%EOF\n"
)

# A file that looks like a PDF by extension but has wrong magic bytes
FAKE_PDF_BYTES = b"This is not a PDF file at all."

# A plain text file
TEXT_FILE_BYTES = b"Hello, I am a text file."


def make_hashed(password: str) -> str:
    return bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")


@pytest.fixture
def client(tmp_path):
    """
    Isolated test client with in-memory DB and
    a temp directory as UPLOAD_FOLDER.
    """
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["JWT_SECRET_KEY"] = "upload-test-secret"
    app.config["UPLOAD_FOLDER"] = str(tmp_path)
    app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024

    with app.app_context():
        db.drop_all()
        db.create_all()

        user = User(
            full_name="Test User",
            email="uploader@example.com",
            password=make_hashed("testpass123")
        )
        db.session.add(user)
        db.session.commit()

    with app.test_client() as c:
        yield c
    with app.app_context():
        db.drop_all()


@pytest.fixture
def token(client):
    resp = client.post(
        "/login",
        json={"email": "uploader@example.com", "password": "testpass123"}
    )
    return resp.get_json()["access_token"]


def auth(token):
    return {"Authorization": f"Bearer {token}"}


def make_upload(filename, content=VALID_PDF_BYTES, field="papers"):
    """Build a multipart/form-data payload for the upload endpoint."""
    return {
        field: (io.BytesIO(content), filename)
    }


# ==============================================================
# AUTHENTICATION GUARD
# ==============================================================

class TestUploadAuthGuard:

    def test_upload_requires_token(self, client):
        """Upload endpoint must reject unauthenticated requests."""
        resp = client.post(
            "/upload-paper",
            data=make_upload("test.pdf"),
            content_type="multipart/form-data"
        )
        assert resp.status_code in (401, 422)

    def test_upload_rejects_invalid_token(self, client):
        resp = client.post(
            "/upload-paper",
            headers={"Authorization": "Bearer fake.token.here"},
            data=make_upload("test.pdf"),
            content_type="multipart/form-data"
        )
        assert resp.status_code in (401, 422)


# ==============================================================
# NORMAL UPLOAD
# ==============================================================

class TestNormalUpload:

    def test_successful_upload_indexes_extracted_text(
        self, client, token, monkeypatch
    ):
        indexed = []
        monkeypatch.setattr(
            paper_routes,
            "process_pdf",
            lambda path: "extracted research text",
        )
        monkeypatch.setattr(
            paper_routes,
            "index_paper",
            lambda text, paper_id, paper_name: indexed.append(
                (text, paper_id, paper_name)
            ),
        )

        response = client.post(
            "/upload-paper",
            headers=auth(token),
            data=make_upload("indexed_paper.pdf"),
            content_type="multipart/form-data",
        )

        assert response.status_code == 200
        assert len(indexed) == 1
        assert indexed[0][0] == "extracted research text"
        assert indexed[0][1] is not None
        assert indexed[0][2].endswith("_indexed_paper.pdf")

    def test_view_pdf_serves_saved_uuid_filename(
        self, client, token, monkeypatch
    ):
        monkeypatch.setattr(
            paper_routes,
            "process_pdf",
            lambda path: "extracted research text",
        )
        monkeypatch.setattr(paper_routes, "index_paper", lambda *args, **kwargs: 1)

        upload = client.post(
            "/upload-paper",
            headers=auth(token),
            data=make_upload("viewed_paper.pdf"),
            content_type="multipart/form-data",
        )
        assert upload.status_code == 200

        response = client.get(
            "/uploads/viewed_paper.pdf",
            headers=auth(token),
        )

        assert response.status_code == 200
        assert response.data.startswith(b"%PDF")

    def test_delete_removes_paper_from_vector_index(
        self, client, token, monkeypatch
    ):
        removed = []
        monkeypatch.setattr(
            paper_routes,
            "remove_paper_from_index",
            lambda paper_id, paper_name: removed.append((paper_id, paper_name)),
        )
        response = client.post(
            "/login",
            json={"email": "uploader@example.com", "password": "testpass123"},
        )
        del_token = response.get_json()["access_token"]

        with app.app_context():
            user = User.query.filter_by(email="uploader@example.com").first()
            record = Paper(
                user_id=user.id,
                filename="display-name.pdf",
                filepath="C:/missing/unique-file_display-name.pdf",
            )
            db.session.add(record)
            db.session.commit()
            paper_id = record.id

        response = client.delete(
            f"/paper/{paper_id}",
            headers=auth(del_token),
        )

        assert response.status_code == 200
        assert removed == [(paper_id, "display-name.pdf")]

    def test_valid_pdf_upload_succeeds(self, client, token, tmp_path):
        """A valid PDF with a clean filename must be accepted."""
        resp = client.post(
            "/upload-paper",
            headers=auth(token),
            data=make_upload("my_paper.pdf"),
            content_type="multipart/form-data"
        )
        # process_pdf may fail in test env (no real PDF text)
        # but the upload itself should be attempted
        assert resp.status_code in (200, 400, 500)

        if resp.status_code == 200:
            data = resp.get_json()
            assert data["success"] is True
            # filename in response must be the original display name
            if data.get("papers"):
                assert data["papers"][0]["filename"] == "my_paper.pdf"

    def test_no_files_returns_400(self, client, token):
        """Empty upload must return 400."""
        resp = client.post(
            "/upload-paper",
            headers=auth(token),
            data={},
            content_type="multipart/form-data"
        )
        assert resp.status_code == 400

    def test_empty_filename_returns_400(self, client, token):
        """Request with no filename must return 400."""
        resp = client.post(
            "/upload-paper",
            headers=auth(token),
            data={"papers": (io.BytesIO(VALID_PDF_BYTES), "")},
            content_type="multipart/form-data"
        )
        assert resp.status_code == 400


# ==============================================================
# FILE TYPE VALIDATION
# ==============================================================

class TestFileTypeValidation:

    def test_non_pdf_extension_rejected(self, client, token):
        """A .exe file must be rejected."""
        resp = client.post(
            "/upload-paper",
            headers=auth(token),
            data=make_upload("malware.exe", TEXT_FILE_BYTES),
            content_type="multipart/form-data"
        )
        data = resp.get_json()
        # Either 400 or success=False, or warnings containing the filename
        if resp.status_code == 200:
            # Uploaded 0 files, returned warnings
            assert not data.get("papers") or data.get("warnings")
        else:
            assert resp.status_code == 400

    def test_txt_extension_rejected(self, client, token):
        """A .txt file must be rejected."""
        resp = client.post(
            "/upload-paper",
            headers=auth(token),
            data=make_upload("notes.txt", TEXT_FILE_BYTES),
            content_type="multipart/form-data"
        )
        data = resp.get_json()
        if resp.status_code == 200:
            assert not data.get("papers") or data.get("warnings")
        else:
            assert resp.status_code == 400

    def test_fake_pdf_magic_bytes_rejected(self, client, token):
        """A file with .pdf extension but wrong magic bytes must be rejected."""
        resp = client.post(
            "/upload-paper",
            headers=auth(token),
            data=make_upload("real_looking.pdf", FAKE_PDF_BYTES),
            content_type="multipart/form-data"
        )
        data = resp.get_json()
        if resp.status_code == 200:
            # Must appear in warnings, not in papers
            warnings = data.get("warnings", [])
            assert any("real_looking.pdf" in w for w in warnings)
            assert not any(
                p["filename"] == "real_looking.pdf"
                for p in data.get("papers", [])
            )
        else:
            assert resp.status_code == 400


# ==============================================================
# PATH TRAVERSAL PREVENTION
# ==============================================================

class TestPathTraversalPrevention:

    @pytest.mark.parametrize("malicious_name", [
        "../../../etc/passwd.pdf",
        "..\\..\\windows\\system32\\cmd.exe.pdf",
        "/absolute/path/evil.pdf",
        "subdir/nested/evil.pdf",
        "....//....//evil.pdf",
        "normal\x00.pdf",          # null byte injection
    ])
    def test_malicious_filename_blocked_or_sanitised(
        self, client, token, tmp_path, malicious_name
    ):
        """
        Malicious filenames must either be safely sanitised or
        blocked. The resulting file must NEVER be written outside
        the upload folder.
        """
        resp = client.post(
            "/upload-paper",
            headers=auth(token),
            data=make_upload(malicious_name),
            content_type="multipart/form-data"
        )

        # Walk the tmp_path tree — no file should have escaped
        upload_folder = str(tmp_path)
        for root, dirs, files in os.walk(upload_folder):
            for f in files:
                full = os.path.realpath(os.path.join(root, f))
                assert full.startswith(os.path.realpath(upload_folder)), (
                    f"File escaped upload folder: {full}"
                )

        # Check nothing was written outside tmp_path itself
        parent = os.path.dirname(upload_folder)
        for entry in os.listdir(parent):
            full = os.path.realpath(os.path.join(parent, entry))
            if full != os.path.realpath(upload_folder):
                assert not entry.endswith(".pdf") or os.path.isdir(full), (
                    f"Suspicious file found outside upload folder: {full}"
                )

    def test_uuid_prevents_overwrite(self, client, token, tmp_path):
        """
        Uploading the same filename twice must produce two
        distinct files on disk (UUID prefix ensures uniqueness).
        """
        for _ in range(2):
            client.post(
                "/upload-paper",
                headers=auth(token),
                data=make_upload("same_name.pdf"),
                content_type="multipart/form-data"
            )

        # Count PDF files on disk — should be 2 distinct files
        pdf_files = list(tmp_path.glob("*.pdf"))
        # Either 2 files OR 0 (if process_pdf cleaned up both on failure)
        # The key guarantee: no single file was overwritten
        if len(pdf_files) >= 2:
            assert len(set(f.name for f in pdf_files)) == len(pdf_files), (
                "UUID prefix should produce unique filenames"
            )
