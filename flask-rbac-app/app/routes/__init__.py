from .auth import auth_bp
from .rbac import rbac_bp
from .organisation import organisation_bp
from app.utils.seed import seed_bp

# Optional: central function for registration
def register_blueprints(app):
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(rbac_bp, url_prefix="/rbac")
    app.register_blueprint(organisation_bp, url_prefix="/org")
    app.register_blueprint(seed_bp, url_prefix="/utils")
