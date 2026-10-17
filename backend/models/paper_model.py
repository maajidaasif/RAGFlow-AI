from database import db
from datetime import datetime, timezone


class Paper(db.Model):
    __tablename__ = "papers"

    id = db.Column(db.Integer, primary_key=True)

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

    filename = db.Column(db.String(255), nullable=False)

    filepath = db.Column(db.String(500), nullable=False)

    uploaded_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc)
    )