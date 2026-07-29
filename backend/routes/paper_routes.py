from flask import Blueprint, request, jsonify, send_from_directory
from database import db
from models.paper_model import Paper
from models.analysis_model import Analysis
from services.pdf_processing import process_pdf
from comparison.paper_comparison import PaperComparisonEngine
from comparison.research_gap import ResearchGapEngine
from collections import Counter
from literature.literature_survey import LiteratureSurveyGenerator

import os

paper = Blueprint("paper", __name__)

UPLOAD_FOLDER = "uploads"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# -----------------------------
# Upload Research Papers
# -----------------------------
@paper.route("/upload-paper", methods=["POST"])
def upload_paper():

    if "papers" not in request.files:
        return jsonify({
            "success": False,
            "message": "No files selected."
        }), 400

    files = request.files.getlist("papers")

    uploaded_papers = []

    for file in files:

        if file.filename == "":
            continue

        if not file.filename.lower().endswith(".pdf"):
            continue

        filepath = os.path.join(
            UPLOAD_FOLDER,
            file.filename
        )

        file.save(filepath)

        process_pdf(filepath)

        paper_data = Paper(
            filename=file.filename,
            filepath=filepath
        )

        db.session.add(paper_data)

        uploaded_papers.append({
            "filename": file.filename,
            "filepath": filepath
        })

    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Research papers uploaded and processed successfully.",
        "papers": uploaded_papers
    }), 200


# -----------------------------
# Get All Uploaded Papers
# -----------------------------
@paper.route("/papers", methods=["GET"])
def get_papers():

    papers = Paper.query.all()

    result = []

    for paper_data in papers:

        result.append({
            "id": paper_data.id,
            "filename": paper_data.filename,
            "filepath": paper_data.filepath,
            "uploaded_at": paper_data.uploaded_at
        })

    return jsonify(result), 200


# -----------------------------
# Delete Paper
# -----------------------------
@paper.route("/paper/<int:paper_id>", methods=["DELETE"])
def delete_paper(paper_id):

    paper_data = Paper.query.get(paper_id)

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

    db.session.delete(paper_data)
    db.session.commit()

    return jsonify({
        "success": True,
        "message": "Paper deleted successfully."
    }), 200


# -----------------------------
# View Uploaded PDF
# -----------------------------
@paper.route("/uploads/<path:filename>", methods=["GET"])
def view_pdf(filename):

    return send_from_directory(
        UPLOAD_FOLDER,
        filename
    )


# -----------------------------
# Compare Papers
# -----------------------------
@paper.route("/compare-papers", methods=["GET"])
def compare_papers():

    comparison_engine = PaperComparisonEngine()

    result = comparison_engine.compare_papers()

    if result["success"]:

        uploaded_papers = Paper.query.all()

        paper_names = ", ".join(
            [paper.filename for paper in uploaded_papers]
        )

        print("=" * 50)
        print("Uploaded Papers :", len(uploaded_papers))
        print("Paper Names :", paper_names)
        print("Detected Domain :", result["domain"])
        print("=" * 50)

        analysis = Analysis(
            analysis_type="Paper Comparison",
            analysis_name="Paper Comparison",
            domain=result["domain"],
            papers=paper_names,
            result=result["comparison"]
        )

        db.session.add(analysis)
        db.session.commit()

    return jsonify(result), 200


# -----------------------------
# Research Gap Detection
# -----------------------------
@paper.route("/research-gap", methods=["GET"])
def research_gap():

    engine = ResearchGapEngine()

    result = engine.detect_research_gap()

    if result["success"]:

        uploaded_papers = Paper.query.all()

        paper_names = ", ".join(
            [paper.filename for paper in uploaded_papers]
        )

        analysis = Analysis(
            analysis_type="Research Gap Detection",
            analysis_name="Research Gap Detection",
              domain=result.get("domain"),
            papers=paper_names,
            result=result["research_gap"]
        )

        db.session.add(analysis)
        db.session.commit()

    return jsonify(result), 200

# -----------------------------
# Literature Survey
# -----------------------------
@paper.route("/literature-survey", methods=["GET"])
def literature_survey():

    generator = LiteratureSurveyGenerator()

    result = generator.generate_literature_survey()

    if not result["success"]:
        return jsonify(result), 400

    uploaded_papers = Paper.query.all()

    paper_names = ", ".join(
        [paper.filename for paper in uploaded_papers]
    )

    analysis = Analysis(
        analysis_type="Literature Survey",
        analysis_name="Literature Survey",
        domain=result["domain"],
        papers=paper_names,
        result=result["literature_survey"]
    )

    db.session.add(analysis)
    db.session.commit()

    return jsonify(result), 200

# -----------------------------
# Get Analysis History
# -----------------------------
@paper.route("/analysis-history", methods=["GET"])
def get_analysis_history():

    analyses = Analysis.query.order_by(
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


# -----------------------------
# Delete Analysis History
# -----------------------------
@paper.route("/analysis-history/<int:analysis_id>", methods=["DELETE"])
def delete_analysis(analysis_id):

    analysis = Analysis.query.get(analysis_id)

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
# -----------------------------
# Dashboard Statistics
# -----------------------------
@paper.route("/dashboard", methods=["GET"])
def dashboard():

    total_papers = Paper.query.count()

    total_analysis = Analysis.query.count()

    paper_comparisons = Analysis.query.filter_by(
        analysis_type="Paper Comparison"
    ).count()

    research_gap = Analysis.query.filter_by(
        analysis_type="Research Gap Detection"
    ).count()

    literature_surveys = Analysis.query.filter_by(
        analysis_type="Literature Survey"
    ).count()

    analyses = Analysis.query.all()

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
            "created_at": item.created_at.strftime("%d-%m-%Y %H:%M")
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