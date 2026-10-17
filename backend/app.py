from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate

from config import Config
from database import db
from models.user_model import User
from models.paper_model import Paper
from models.analysis_model import Analysis

from routes.auth_routes import auth
from routes.paper_routes import paper
from routes.report_routes import report_bp
from routes.literature_routes import literature
from routes.chat_routes import chat_bp

from services.resource_monitor import (
    check_available_ram,
    get_ram_status
)

from services.application_initializer import (
    ApplicationInitializer
)


app = Flask(__name__)
app.config.from_object(Config)

CORS(
    app,
    resources={
        r"/*": {
            "origins": [
                "http://localhost:5173",
                "http://127.0.0.1:5173",
            ]
        }
    }
)

jwt = JWTManager(app)

db.init_app(app)
migrate = Migrate(app, db)


# ============================================================
# ERROR HANDLERS
# ============================================================

@app.errorhandler(413)
def request_entity_too_large(e):
    return jsonify({
        "success": False,
        "message": "File too large. Maximum upload size is 50 MB per request."
    }), 413


# ============================================================
# REGISTER BLUEPRINTS
# ============================================================

app.register_blueprint(auth)
app.register_blueprint(paper)
app.register_blueprint(report_bp)
app.register_blueprint(literature)
app.register_blueprint(chat_bp)


# ============================================================
# HOME
# ============================================================

@app.route("/")
def home():

    return "ResearchMind AI Backend is Running Successfully!"


# ============================================================
# MODULE 13 - SYSTEM RESOURCE STATUS
# ============================================================

@app.route("/system-status")
def system_status():

    ram = check_available_ram()

    status = get_ram_status(
        ram,
        4
    )

    return {
        "available_ram": round(ram, 2),
        "ram_status": status
    }


# ============================================================
# APPLICATION STARTUP
# MODULE 14 - APPLICATION INITIALIZATION & SAFETY CONTROL
# ============================================================

if __name__ == "__main__":
    # --------------------------------------------------------
    # Initialize ResearchMind AI
    # --------------------------------------------------------

    initializer = ApplicationInitializer()


    # --------------------------------------------------------
    # Run Module 14 startup sequence
    # --------------------------------------------------------

    if not initializer.initialize():

        print(
            "\nResearchMind AI 2.0 could not start safely."
        )

        exit(1)


    # --------------------------------------------------------
    # Start Flask application
    # --------------------------------------------------------

    app.run(
        debug=app.config["DEBUG"],
        use_reloader=False
    )