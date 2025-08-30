from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models import Role, Permission, User
from app.utils.decorators import roles_required, permissions_required

rbac_bp = Blueprint("rbac", __name__)

# ---------- role-protected examples ----------
@rbac_bp.get("/admin/dashboard")
@roles_required("Admin")
def admin_dashboard():
    return {"message": "Admin dashboard"}

@rbac_bp.get("/editor/dashboard")
@roles_required("Admin", "Editor")
def editor_dashboard():
    return {"message": "Editor dashboard"}

@rbac_bp.get("/user/dashboard")
@roles_required("Admin", "Editor", "User")
def user_dashboard():
    return {"message": "User dashboard"}

# ---------- permission-protected examples ----------
@rbac_bp.get("/users")
@permissions_required("view_users")
def list_users():
    users = [{"id": u.id, "username": u.username, "role": u.role.name if u.role else None}
             for u in User.query.all()]
    return {"users": users}

# ---------- CRUD: Roles ----------
@rbac_bp.get("/roles")
@roles_required("Admin")
def get_roles():
    roles = Role.query.all()
    return {"roles": [{"id": r.id, "name": r.name, "description": r.description} for r in roles]}

@rbac_bp.post("/roles")
@roles_required("Admin")
def create_role():
    data = request.get_json() or {}
    name = data.get("name")
    description = data.get("description", "")
    if not name:
        return {"error": "name required"}, 400
    if Role.query.filter_by(name=name).first():
        return {"error": "Role exists"}, 400
    r = Role(name=name, description=description)
    db.session.add(r); db.session.commit()
    return {"id": r.id, "name": r.name}, 201

@rbac_bp.put("/roles/<int:role_id>")
@roles_required("Admin")
def update_role(role_id):
    data = request.get_json() or {}
    r = Role.query.get_or_404(role_id)
    r.name = data.get("name", r.name)
    r.description = data.get("description", r.description)
    db.session.commit()
    return {"message": "updated"}

@rbac_bp.delete("/roles/<int:role_id>")
@roles_required("Admin")
def delete_role(role_id):
    r = Role.query.get_or_404(role_id)
    if User.query.filter_by(role_id=r.id).first():
        return {"error": "Role assigned to users"}, 400
    db.session.delete(r); db.session.commit()
    return {"message": "deleted"}

# ---------- CRUD: Permissions ----------
@rbac_bp.get("/permissions")
@roles_required("Admin")
def get_permissions():
    perms = Permission.query.all()
    return {"permissions": [{"id": p.id, "name": p.name, "description": p.description} for p in perms]}

@rbac_bp.post("/permissions")
@roles_required("Admin")
def create_permission():
    data = request.get_json() or {}
    name = data.get("name")
    desc = data.get("description", "")
    if not name:
        return {"error": "name required"}, 400
    if Permission.query.filter_by(name=name).first():
        return {"error": "Permission exists"}, 400
    p = Permission(name=name, description=desc)
    db.session.add(p); db.session.commit()
    return {"id": p.id, "name": p.name}, 201

@rbac_bp.put("/permissions/<int:perm_id>")
@roles_required("Admin")
def update_permission(perm_id):
    data = request.get_json() or {}
    p = Permission.query.get_or_404(perm_id)
    p.name = data.get("name", p.name)
    p.description = data.get("description", p.description)
    db.session.commit()
    return {"message": "updated"}

@rbac_bp.delete("/permissions/<int:perm_id>")
@roles_required("Admin")
def delete_permission(perm_id):
    p = Permission.query.get_or_404(perm_id)
    db.session.delete(p); db.session.commit()
    return {"message": "deleted"}

# ---------- Assign permissions to a role ----------
@rbac_bp.post("/roles/<int:role_id>/permissions")
@roles_required("Admin")
def set_role_permissions(role_id):
    data = request.get_json() or {}   # { "permissions": ["view_users", "create_user"] }
    names = data.get("permissions", [])
    role = Role.query.get_or_404(role_id)
    perms = Permission.query.filter(Permission.name.in_(names)).all()
    role.permissions = perms
    db.session.commit()
    return {"message": "permissions set", "count": len(perms)}
