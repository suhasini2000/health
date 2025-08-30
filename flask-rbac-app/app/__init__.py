
from flask import Flask
from flask_cors import CORS
from app.extensions import db
from flask_jwt_extended import JWTManager


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object('config.Config')

    # Bind db to app
    db.init_app(app)

    # Import & register blueprints
    from app.routes import auth_bp, rbac_bp, organisation_bp
    from app.utils.seed import seed_bp

    JWTManager(app)


    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(rbac_bp, url_prefix="/rbac")
    app.register_blueprint(organisation_bp, url_prefix="/org")
    app.register_blueprint(seed_bp, url_prefix="/utils")

    # Enable CORS for frontend (localhost:3000)
    CORS(app, origins=["http://localhost:3000"], supports_credentials=True)

    # Create tables once app context is available
    with app.app_context():
        db.create_all()

    return app

