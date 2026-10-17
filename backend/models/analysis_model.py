from database import db
from datetime import datetime, timezone


class Analysis(db.Model):

    __tablename__ = "analysis_history"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    # --------------------------------------------------------
    # Owner — nullable so existing records survive migration.
    # New records always have user_id set from JWT identity.
    # --------------------------------------------------------
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=True,
        index=True
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
        default=lambda: datetime.now(timezone.utc)
    )