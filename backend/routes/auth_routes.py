import re

from flask import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity
)

from database import db
from models.user_model import User

import bcrypt

auth = Blueprint("auth", __name__)


# ============================================================
# VALIDATION CONSTANTS
# ============================================================

# Minimum password length enforced on registration.
# Changing this value does NOT retroactively invalidate existing
# accounts — it only applies to new registrations.
_MIN_PASSWORD_LENGTH = 8

# Simple but reasonable email pattern:
#   local-part @ domain . tld
# Rejects addresses that are obviously malformed without being
# a full RFC-5321 parser.
_EMAIL_RE = re.compile(
    r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$'
)


# ============================================================
# VALIDATION HELPER
# ============================================================

def _parse_auth_body(required_fields):
    """Parse and validate a JSON auth request body.

    Returns (data_dict, None) on success or (None, error_response)
    where error_response is a ready-made Flask response tuple.

    Parameters
    ----------
    required_fields : list[str]
        Field names that must be present and non-empty strings.
    """

    # ── 1. Require JSON content-type and a parseable body ────────────
    data = request.get_json(silent=True)

    if data is None:
        return None, (
            jsonify({
                "success": False,
                "message": "Request body must be valid JSON."
            }),
            400
        )

    if not isinstance(data, dict):
        return None, (
            jsonify({
                "success": False,
                "message": "Request body must be a JSON object."
            }),
            400
        )

    # ── 2. Check every required field is present and is a string ─────
    for field in required_fields:

        if field not in data:
            return None, (
                jsonify({
                    "success": False,
                    "message": f"Missing required field: '{field}'."
                }),
                400
            )

        if not isinstance(data[field], str):
            return None, (
                jsonify({
                    "success": False,
                    "message": (
                        f"Field '{field}' must be a string, "
                        f"got {type(data[field]).__name__}."
                    )
                }),
                400
            )

        if not data[field].strip():
            return None, (
                jsonify({
                    "success": False,
                    "message": f"Field '{field}' must not be blank."
                }),
                400
            )

    return data, None




# ==========================
# Register API
# ==========================
@auth.route("/register", methods=["POST"])
def register():

    # ── Parse & validate body ────────────────────────────────────────
    data, err = _parse_auth_body(["full_name", "email", "password"])

    if err:
        return err

    full_name = data["full_name"].strip()
    email     = data["email"].strip().lower()
    password  = data["password"]          # do NOT strip passwords

    # ── Email format ─────────────────────────────────────────────────
    if not _EMAIL_RE.match(email):
        return jsonify({
            "success": False,
            "message": "Invalid email address format."
        }), 400

    # ── Email length (DB column is 120 chars) ─────────────────────────
    if len(email) > 120:
        return jsonify({
            "success": False,
            "message": "Email address is too long (max 120 characters)."
        }), 400

    # ── Full name length (DB column is 100 chars) ─────────────────────
    if len(full_name) > 100:
        return jsonify({
            "success": False,
            "message": "Full name is too long (max 100 characters)."
        }), 400

    # ── Password minimum length ───────────────────────────────────────
    if len(password) < _MIN_PASSWORD_LENGTH:
        return jsonify({
            "success": False,
            "message": (
                f"Password must be at least {_MIN_PASSWORD_LENGTH} "
                "characters long."
            )
        }), 400

    # ── Duplicate email check ─────────────────────────────────────────
    existing_user = User.query.filter_by(email=email).first()

    if existing_user:
        return jsonify({
            "message": "Email already registered"
        }), 409

    # ── Hash & persist ────────────────────────────────────────────────
    hashed_password = bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")

    new_user = User(
        full_name=full_name,
        email=email,
        password=hashed_password
    )

    db.session.add(new_user)
    db.session.commit()

    return jsonify({
        "message": "User Registered Successfully"
    }), 201


# ==========================
# Login API
# ==========================
@auth.route("/login", methods=["POST"])
def login():

    # ── Parse & validate body ────────────────────────────────────────
    data, err = _parse_auth_body(["email", "password"])

    if err:
        return err

    email    = data["email"].strip().lower()
    password = data["password"]

    # ── Email format ─────────────────────────────────────────────────
    if not _EMAIL_RE.match(email):
        return jsonify({
            "success": False,
            "message": "Invalid email address format."
        }), 400

    # ── Credential check ─────────────────────────────────────────────
    # Use a generic message for both bad email and bad password to
    # prevent user-enumeration attacks.
    _INVALID_CREDENTIALS = "Invalid email or password."

    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify({
            "message": _INVALID_CREDENTIALS
        }), 401

    if not bcrypt.checkpw(
        password.encode("utf-8"),
        user.password.encode("utf-8")
    ):
        return jsonify({
            "message": _INVALID_CREDENTIALS
        }), 401

    access_token = create_access_token(identity=user.email)

    return jsonify({

        "message": "Login Successful",

        "access_token": access_token,

        "user": {

            "full_name": user.full_name,

            "email": user.email,

            "role": "Researcher"

        }

    }), 200


# ==========================
# Protected Profile API
# ==========================
@auth.route("/profile", methods=["GET"])
@jwt_required()
def profile():

    current_user = get_jwt_identity()

    user = User.query.filter_by(email=current_user).first()

    return jsonify({

        "message": "Protected Route Accessed Successfully",

        "user": {

            "full_name": user.full_name,

            "email": user.email,

            "role": "Researcher"

        }

    }), 200