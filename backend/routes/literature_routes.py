from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from database import db
from models.user_model import User
from models.paper_model import Paper
from models.analysis_model import Analysis

from literature.literature_survey import (
    LiteratureSurveyGenerator
)

literature = Blueprint(
    "literature",
    __name__
)


def get_current_user():
    """Return the User object for the authenticated request."""
    email = get_jwt_identity()
    return User.query.filter_by(email=email).first()


# -----------------------------
# Literature Survey Generator
# -----------------------------
@literature.route(
    "/literature-survey",
    methods=["GET"]
)
@jwt_required()
def generate_literature_survey():

    current_user = get_current_user()

    if current_user is None:
        return jsonify({"success": False, "message": "User not found."}), 404

    # Create Literature Survey Engine
    engine = LiteratureSurveyGenerator()

    # Generate Literature Survey
    result = engine.generate_literature_survey()

    # If generation failed
    if not result["success"]:
        return jsonify(result), 404

    # Get the current user's uploaded paper names only
    uploaded_papers = Paper.query.filter_by(
        user_id=current_user.id
    ).all()

    paper_names = ", ".join(
        [
            paper.filename
            for paper in uploaded_papers
        ]
    )

    # Save into Analysis History linked to this user
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

    return jsonify({

        "success": True,

        "domain": result["domain"],

        "literature_survey": result["literature_survey"]

    }), 200