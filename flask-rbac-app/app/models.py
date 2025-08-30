from app.extensions import db
from werkzeug.security import generate_password_hash, check_password_hash

# Association table Role <-> Permission
role_permissions = db.Table(
    "role_permissions",
    db.Column("role_id", db.Integer, db.ForeignKey("roles.id"), primary_key=True),
    db.Column("permission_id", db.Integer, db.ForeignKey("permissions.id"), primary_key=True),
)

class Organisation(db.Model):
    __tablename__ = "organisations"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    details = db.Column(db.String(255))

class Role(db.Model):
    __tablename__ = "roles"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)   # Admin, Editor, User
    description = db.Column(db.String(255))
    permissions = db.relationship("Permission", secondary=role_permissions, backref="roles")

class Permission(db.Model):
    __tablename__ = "permissions"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(255))

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(10), default="active")

    role_id = db.Column(db.Integer, db.ForeignKey("roles.id"))
    organisation_id = db.Column(db.Integer, db.ForeignKey("organisations.id"))

    role = db.relationship("Role")
    organisation = db.relationship("Organisation")

    # helpers
    def set_password(self, raw: str):
        self.password_hash = generate_password_hash(raw)

    def check_password(self, raw: str) -> bool:
        return check_password_hash(self.password_hash, raw)

    def check_admin(self) -> bool:
        """Return True if user has Admin role, else False."""
        return self.role is not None and self.role.name == "Admin"
