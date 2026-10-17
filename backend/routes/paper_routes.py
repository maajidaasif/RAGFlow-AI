from flask import Blueprint, request, jsonify, send_from_directory, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename

from database import db
from models.user_model import User
from models.paper_model import Paper
from models.analysis_model import Analysis

from services.pdf_processing import process_pdf
from services.indexing import index_paper, remove_paper_from_index

from comparison.paper_comparison import PaperComparisonEngine
from comparison.research_gap import ResearchGapEngine

from literature.literature_survey import LiteratureSurveyGenerator

from collections import Counter

import os
import uuid


paper = Blueprint("paper", __name__)

# UPLOAD_FOLDER is set from app.config (absolute path).
# Fallback only used when running tests with SQLite in-memory.
_FALLBACK_UPLOAD_FOLDER = os.path.join(
    os.path.abspath(os.path.dirname(__file__)), "..", "uploads"
)


def _get_upload_folder():
    """Return the absolute upload directory from app config."""
    folder = current_app.config.get(
        "UPLOAD_FOLDER", _FALLBACK_UPLOAD_FOLDER
    )
    os.makedirs(folder, exist_ok=True)
    return os.path.abspath(folder)


# PDF magic bytes — first 4 bytes of every valid PDF file
_PDF_MAGIC = b"%PDF"


# =========================================================
# HELPER — resolve current user from JWT identity (email)
# =========================================================

def get_current_user():
    """Return the User object for the authenticated request."""
    email = get_jwt_identity()
    return User.query.filter_by(email=email).first()


# =========================================================
# Upload Research Papers
# =========================================================
@paper.route("/upload-paper", methods=["POST"])
@jwt_required()
def upload_paper():

    current_user = get_current_user()

    if current_user is None:
        return jsonify({"success": False, "message": "User not found."}), 404

    if "papers" not in request.files:
        return jsonify({
            "success": False,
            "message": "No files selected."
        }), 400

    files = request.files.getlist("papers")

    if not files or all(f.filename == "" for f in files):
        return jsonify({
            "success": False,
            "message": "No files selected."
        }), 400

    upload_folder = _get_upload_folder()
    uploaded_papers = []
    errors = []

    for file in files:

        # ── 1. Skip empty slots ───────────────────────────
        if not file or file.filename == "":
            continue

        original_name = file.filename

        # ── 2. Extension whitelist ────────────────────────
        if not original_name.lower().endswith(".pdf"):
            errors.append(
                f"{original_name}: only PDF files are allowed."
            )
            continue

        # ── 3. Sanitise with secure_filename ─────────────
        safe_base = secure_filename(original_name)

        if not safe_base:
            errors.append(
                f"{original_name}: filename is invalid after sanitisation."
            )
            continue

        # ── 4. UUID-based server filename (no collisions) ─
        server_filename = f"{uuid.uuid4().hex}_{safe_base}"

        # ── 5. Resolve and confine the final path ─────────
        final_path = os.path.realpath(
            os.path.join(upload_folder, server_filename)
        )

        # Ensure resolved path stays inside upload_folder
        if os.path.commonpath([final_path, upload_folder]) != upload_folder:
            errors.append(
                f"{original_name}: path traversal attempt blocked."
            )
            continue

        # ── 6. Save file to disk ──────────────────────────
        try:
            file.save(final_path)
        except Exception as e:
            errors.append(
                f"{original_name}: failed to save file."
            )
            continue

        # ── 7. Validate PDF magic bytes ───────────────────
        try:
            with open(final_path, "rb") as f_check:
                header = f_check.read(4)
            if header != _PDF_MAGIC:
                os.remove(final_path)
                errors.append(
                    f"{original_name}: file content is not a valid PDF."
                )
                continue
        except Exception:
            if os.path.exists(final_path):
                os.remove(final_path)
            errors.append(
                f"{original_name}: could not verify file content."
            )
            continue

        # ── 8. Process PDF (extract + index) ─────────────
        try:
            extracted_text = process_pdf(final_path)
        except Exception as e:
            # Clean up the saved file on processing failure
            if os.path.exists(final_path):
                os.remove(final_path)
            errors.append(
                f"{original_name}: PDF processing failed — {str(e)}"
            )
            continue

        # ── 9. Persist Paper record ───────────────────────
        paper_data = Paper(
            user_id=current_user.id,
            filename=original_name,        # human-readable display name
            filepath=final_path            # absolute server-side path
        )

        db.session.add(paper_data)
        db.session.flush()

        try:
            index_paper(
                extracted_text,
                paper_id=paper_data.id,
                paper_name=server_filename
            )
        except Exception as e:
            db.session.delete(paper_data)
            if os.path.exists(final_path):
                os.remove(final_path)
            errors.append(
                f"{original_name}: indexing failed — {str(e)}"
            )
            continue

        uploaded_papers.append({
            "filename": original_name,
            "filepath": final_path
        })

    if not uploaded_papers and not errors:
        return jsonify({
            "success": False,
            "message": "No valid PDF files were found in the request."
        }), 400

    db.session.commit()

    response = {
        "success": True,
        "message": "Research papers uploaded and processed successfully.",
        "papers": uploaded_papers
    }

    if errors:
        response["warnings"] = errors

    return jsonify(response), 200


# =========================================================
# Get All Uploaded Papers (current user only)
# =========================================================
@paper.route("/papers", methods=["GET"])
@jwt_required()
def get_papers():

    current_user = get_current_user()

    if current_user is None:
        return jsonify({"message": "User not found."}), 404

    papers = Paper.query.filter_by(user_id=current_user.id).all()

    result = []

    for paper_data in papers:

        result.append({
            "id": paper_data.id,
            "filename": paper_data.filename,
            "filepath": paper_data.filepath,
            "uploaded_at": paper_data.uploaded_at
        })

    return jsonify(result), 200


# =========================================================
# Delete Paper (current user only)
# =========================================================
@paper.route("/paper/<int:paper_id>", methods=["DELETE"])
@jwt_required()
def delete_paper(paper_id):

    current_user = get_current_user()

    if current_user is None:
        return jsonify({"success": False, "message": "User not found."}), 404

    # Filter by user_id — prevents deleting another user's paper
    paper_data = Paper.query.filter_by(
        id=paper_id,
        user_id=current_user.id
    ).first()

    if paper_data is None:
        return jsonify({
            "success": False,
            "message": "Paper not found."
        }), 404

    if os.path.exists(paper_data.filepath):
        os.remove(paper_data.filepath)

    processed_file = os.path.join(
        "processed",
        os.path.basename(
            paper_data.filepath
        ).replace(".pdf", ".txt")
    )

    if os.path.exists(processed_file):
        os.remove(processed_file)

    remove_paper_from_index(paper_id, paper_data.filename)

    db.session.delete(paper_data)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Paper deleted successfully."
    }), 200


# =========================================================
# View Uploaded PDF (current user only)
# =========================================================
@paper.route("/uploads/<path:filename>", methods=["GET"])
@jwt_required()
def view_pdf(filename):

    current_user = get_current_user()

    if current_user is None:
        return jsonify({"message": "User not found."}), 404

    # Confirm the requesting user owns a paper with this filename
    owned = Paper.query.filter_by(
        filename=filename,
        user_id=current_user.id
    ).first()

    if owned is None:
        return jsonify({"message": "Not found."}), 404

    return send_from_directory(
        _get_upload_folder(),
        os.path.basename(owned.filepath)
    )


# =========================================================
# Compare Papers (current user's papers only)
# =========================================================
@paper.route("/compare-papers", methods=["GET"])
@jwt_required()
def compare_papers():

    current_user = get_current_user()

    if current_user is None:
        return jsonify({"success": False, "message": "User not found."}), 404

    try:
        limit = int(request.args.get("limit", 5))
    except ValueError:
        return jsonify({"success": False, "message": "limit must be an integer."}), 400

    if limit < 1 or limit > 5:
        return jsonify({"success": False, "message": "limit must be between 1 and 5."}), 400

    owned_query = Paper.query.filter_by(user_id=current_user.id)
    requested_ids = request.args.get("paper_ids")

    if requested_ids:
        try:
            paper_ids = [int(value) for value in requested_ids.split(",")]
        except ValueError:
            return jsonify({"success": False, "message": "paper_ids must be comma-separated integers."}), 400

        if not paper_ids or len(paper_ids) > limit or len(set(paper_ids)) != len(paper_ids):
            return jsonify({"success": False, "message": f"Select between 1 and {limit} unique papers."}), 400

        uploaded_papers = owned_query.filter(Paper.id.in_(paper_ids)).all()
        if len(uploaded_papers) != len(paper_ids):
            return jsonify({"success": False, "message": "One or more papers were not found."}), 404
    else:
        uploaded_papers = owned_query.order_by(Paper.id.desc()).limit(limit).all()

    comparison_engine = PaperComparisonEngine()
    result = comparison_engine.compare_papers(
        paper_names=[os.path.basename(paper.filepath) for paper in uploaded_papers],
        max_papers=limit
    )

    if result["success"]:

        paper_names = ", ".join(
            [p.filename for p in uploaded_papers]
        )

        print("=" * 50)
        print("Uploaded Papers :", len(uploaded_papers))
        print("Paper Names :", paper_names)
        print("Detected Domain :", result["domain"])
        print("=" * 50)

        analysis = Analysis(
            user_id=current_user.id,
            analysis_type="Paper Comparison",
            analysis_name="Paper Comparison",
            domain=result["domain"],
            papers=paper_names,
            result=result["comparison"]
        )

        db.session.add(analysis)
        db.session.commit()

    return jsonify(result), 200


# =========================================================
# Research Gap Detection (current user's papers only)
# =========================================================
@paper.route("/research-gap", methods=["GET"])
@jwt_required()
def research_gap():

    current_user = get_current_user()

    if current_user is None:
        return jsonify({"success": False, "message": "User not found."}), 404

    engine = ResearchGapEngine()

    result = engine.detect_research_gap()

    if result["success"]:

        uploaded_papers = Paper.query.filter_by(
            user_id=current_user.id
        ).all()

        paper_names = ", ".join(
            [p.filename for p in uploaded_papers]
        )

        analysis = Analysis(
            user_id=current_user.id,
            analysis_type="Research Gap Detection",
            analysis_name="Research Gap Detection",
            domain=result.get("domain"),
            papers=paper_names,
            result=result["research_gap"]
        )

        db.session.add(analysis)
        db.session.commit()

    return jsonify(result), 200


# =========================================================
# Literature Survey (current user's papers only)
# =========================================================
@paper.route("/literature-survey", methods=["GET"])
@jwt_required()
def literature_survey():

    current_user = get_current_user()

    if current_user is None:
        return jsonify({"success": False, "message": "User not found."}), 404

    generator = LiteratureSurveyGenerator()

    result = generator.generate_literature_survey()

    if not result["success"]:
        return jsonify(result), 400

    uploaded_papers = Paper.query.filter_by(
        user_id=current_user.id
    ).all()

    paper_names = ", ".join(
        [p.filename for p in uploaded_papers]
    )

    analysis = Analysis(
        user_id=current_user.id,
        analysis_type="Literature Survey",
        analysis_name="Literature Survey",
        domain=result["domain"],
        papers=paper_names,
        result=result["literature_survey"]
    )

    db.session.add(analysis)
    db.session.commit()

    return jsonify(result), 200


# =========================================================
# Get Analysis History (current user only)
# =========================================================
@paper.route("/analysis-history", methods=["GET"])
@jwt_required()
def get_analysis_history():

    current_user = get_current_user()

    if current_user is None:
        return jsonify({"message": "User not found."}), 404

    analyses = Analysis.query.filter_by(
        user_id=current_user.id
    ).order_by(
        Analysis.created_at.desc()
    ).all()

    result = []

    for item in analyses:

        result.append({
            "id": item.id,
            "analysis_type": item.analysis_type,
            "analysis_name": item.analysis_name,
            "domain": item.domain,
            "papers": item.papers,
            "result": item.result,
            "created_at": item.created_at
        })

    return jsonify(result), 200


# =========================================================
# Delete Analysis (current user only)
# =========================================================
@paper.route("/analysis-history/<int:analysis_id>", methods=["DELETE"])
@jwt_required()
def delete_analysis(analysis_id):

    current_user = get_current_user()

    if current_user is None:
        return jsonify({"success": False, "message": "User not found."}), 404

    # Filter by user_id — prevents deleting another user's analysis
    analysis = Analysis.query.filter_by(
        id=analysis_id,
        user_id=current_user.id
    ).first()

    if analysis is None:
        return jsonify({
            "success": False,
            "message": "Analysis not found."
        }), 404

    db.session.delete(analysis)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Analysis deleted successfully."
    }), 200


# =========================================================
# Dashboard Statistics (current user only)
# =========================================================
@paper.route("/dashboard", methods=["GET"])
@jwt_required()
def dashboard():

    current_user = get_current_user()

    if current_user is None:
        return jsonify({"message": "User not found."}), 404

    uid = current_user.id

    total_papers = Paper.query.filter_by(user_id=uid).count()

    total_analysis = Analysis.query.filter_by(user_id=uid).count()

    paper_comparisons = Analysis.query.filter_by(
        user_id=uid,
        analysis_type="Paper Comparison"
    ).count()

    research_gap = Analysis.query.filter_by(
        user_id=uid,
        analysis_type="Research Gap Detection"
    ).count()

    literature_surveys = Analysis.query.filter_by(
        user_id=uid,
        analysis_type="Literature Survey"
    ).count()

    analyses = Analysis.query.filter_by(user_id=uid).all()

    domain_counter = Counter()

    for analysis in analyses:

        if analysis.domain:
            domain_counter[analysis.domain] += 1

    domains = []

    for domain, count in domain_counter.items():

        domains.append({
            "domain": domain,
            "count": count
        })

    recent_activity = []

    recent = (
        Analysis.query
        .filter_by(user_id=uid)
        .order_by(Analysis.created_at.desc())
        .limit(5)
        .all()
    )

    for item in recent:

        recent_activity.append({
            "id": item.id,
            "analysis_name": item.analysis_name,
            "analysis_type": item.analysis_type,
            "domain": item.domain,
            "created_at": item.created_at.strftime(
                "%d-%m-%Y %H:%M"
            )
        })

    return jsonify({
        "total_papers": total_papers,
        "total_analysis": total_analysis,
        "paper_comparisons": paper_comparisons,
        "research_gap": research_gap,
        "literature_surveys": literature_surveys,
        "domains": domains,
        "recent_activity": recent_activity
    })