from flask import Blueprint

organisation_bp = Blueprint("organisation", __name__)

@organisation_bp.route("/info")
def info():
    return {"message": "Organisation route working!"}
