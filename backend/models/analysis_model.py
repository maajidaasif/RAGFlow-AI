from database import db
from datetime import datetime


class Analysis(db.Model):

    __tablename__ = "analysis_history"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    analysis_type = db.Column(
        db.String(100),
        nullable=False
    )

    analysis_name = db.Column(
        db.String(200),
        nullable=False
    )

    # Research Domain
    domain = db.Column(
        db.String(200),
        nullable=True
    )

    papers = db.Column(
        db.Text,
        nullable=False
    )

    result = db.Column(
        db.Text,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )