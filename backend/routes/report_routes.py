from flask import Blueprint, jsonify

from services.report_generator import ReportGenerator

report_bp = Blueprint(
    "report",
    __name__
)

generator = ReportGenerator()


@report_bp.route(
    "/generate-report",
    methods=["POST"]
)
def generate_report():

    try:

        report = generator.generate_report()

        return jsonify({

            "success": True,

            "report": report

        }), 200

    except Exception as e:

        print("Report Generation Error:", e)

        return jsonify({

            "success": False,

            "message": str(e)

        }), 500