
from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models import Role, Permission, Organisation, User

seed_bp = Blueprint("seed", __name__)

@seed_bp.post("/seed")
def seed():
    # Organisation
    if not Organisation.query.filter_by(name="Default Org").first():
        db.session.add(Organisation(name="Default Org", details="Sample org"))

    # Canonical permissions
    perm_names = [
        "view_users","create_user","update_user","delete_user",
        "view_roles","create_role","update_role","delete_role",
        "view_permissions","create_permission","update_permission","delete_permission"
    ]
    perm_objs = {}
    for n in perm_names:
        p = Permission.query.filter_by(name=n).first()
        if not p:
            p = Permission(name=n, description=n.replace("_"," ").title())
            db.session.add(p)
        perm_objs[n] = p

    # Roles
    def ensure_role(name, description, names):
        r = Role.query.filter_by(name=name).first()
        if not r:
            r = Role(name=name, description=description)
            db.session.add(r); db.session.flush()
        r.permissions = [perm_objs[x] for x in names]
        return r

    ensure_role("Admin", "Full access", perm_names)
    ensure_role("Editor", "Content editor", ["view_users","create_user","update_user"])
    ensure_role("User", "Basic user", [])

    db.session.commit()
    return {"message": "Seeded roles/permissions/organisation"}, 201


# Endpoint to create a default admin user
@seed_bp.route("/create_admin", methods=["POST"])
def create_admin():
    data = request.get_json() or {}
    username = data.get("username", "admin")
    password = data.get("password", "admin123")
    email = data.get("email", "admin@example.com")
    if User.query.filter_by(username=username).first():
        return jsonify({"error": "User already exists"}), 400
    admin_role = Role.query.filter_by(name="Admin").first()
    org = Organisation.query.first()
    user = User(username=username, email=email, role=admin_role, organisation=org)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return jsonify({"message": "Admin user created", "username": username, "password": password}), 201
