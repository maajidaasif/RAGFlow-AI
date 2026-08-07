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
from routes.literature_routes import literature
from routes.report_routes import report_bp

app = Flask(__name__)
app.config.from_object(Config)

CORS(
    app,
    resources={r"/*": {"origins": "http://localhost:5173"}}
)

jwt = JWTManager(app)

db.init_app(app)

# Register Blueprints
app.register_blueprint(auth)
app.register_blueprint(paper)
app.register_blueprint(literature)
app.register_blueprint(report_bp)


@app.route("/")
def home():
    return "ResearchMind AI Backend is Running Successfully!"


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)