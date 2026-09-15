from flask import Blueprint, request, jsonify

from .generator import ReportGenerator

report_bp = Blueprint("report", __name__)

generator = ReportGenerator()


@report_bp.route("/generate-report", methods=["POST"])
def generate_report():

    data = request.get_json()

    literature_survey = data.get("literature_survey", "")
    comparison = data.get("comparison", "")
    research_gap = data.get("research_gap", "")

    report = generator.generate_report(
        literature_survey,
        comparison,
        research_gap
    )

    return jsonify({
        "success": True,
        "report": report
    })