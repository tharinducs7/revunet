from flask import Flask
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}})

    # Register Blueprints
    from app.routes import main_bp
    app.register_blueprint(main_bp)

    return app
