from flask import Blueprint, jsonify

from database import db
from models.paper_model import Paper
from models.analysis_model import Analysis

from literature.literature_survey import (
    LiteratureSurveyGenerator
)

literature = Blueprint(
    "literature",
    __name__
)


# -----------------------------
# Literature Survey Generator
# -----------------------------
@literature.route(
    "/literature-survey",
    methods=["GET"]
)
def generate_literature_survey():

    # Create Literature Survey Engine
    engine = LiteratureSurveyGenerator()

    # Generate Literature Survey
    result = engine.generate_literature_survey()

    # If generation failed
    if not result["success"]:
        return jsonify(result), 404

    # Get uploaded paper names
    uploaded_papers = Paper.query.all()

    paper_names = ", ".join(
        [
            paper.filename
            for paper in uploaded_papers
        ]
    )

    # Save into Analysis History
    analysis = Analysis(

        analysis_type="Literature Survey",

        analysis_name="Literature Survey",

        domain=result["domain"],

        papers=paper_names,

        result=result["literature_survey"]

    )

    db.session.add(analysis)
    db.session.commit()

    return jsonify({

        "success": True,

        "domain": result["domain"],

        "literature_survey": result["literature_survey"]

    }), 200