from functools import wraps
from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import User

def roles_required(*allowed_roles):
    """
    Usage: @roles_required("Admin") or @roles_required("Admin","Editor")
    """
    def outer(fn):
        @wraps(fn)
        @jwt_required()
        def wrapper(*args, **kwargs):
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            if not user or not user.role or user.role.name not in allowed_roles:
                return jsonify({"error": "Forbidden (role)"}), 403
            return fn(*args, **kwargs)
        return wrapper
    return outer

def permissions_required(*needed_perms):
    """
    Usage: @permissions_required("view_users","create_user")
    """
    def outer(fn):
        @wraps(fn)
        @jwt_required()
        def wrapper(*args, **kwargs):
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            if not user or not user.role:
                return jsonify({"error": "Forbidden"}), 403
            role_perms = {p.name for p in user.role.permissions}
            if not set(needed_perms).issubset(role_perms):
                return jsonify({"error": "Forbidden (permission)"}), 403
            return fn(*args, **kwargs)
        return wrapper
    return outer
