from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager

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
    resources={r"/*": {"origins": "http://localhost:5173"}}
)

jwt = JWTManager(app)

db.init_app(app)


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
    # Create database tables
    # --------------------------------------------------------

    with app.app_context():

        db.create_all()


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
        debug=False,
        use_reloader=False
)