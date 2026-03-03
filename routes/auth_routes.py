import secrets
from flask import Blueprint, request, jsonify
from models.user import User

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

# ── In-memory session store (simple – suitable for single-worker deployment) ──
# Maps token → user dict
_sessions = {}

def get_current_user():
    """Extract user from Bearer token in Authorization header."""
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return None
    token = auth[7:]
    return _sessions.get(token)

@auth_bp.route("/signup", methods=["POST"])
def signup():
    body     = request.get_json(silent=True) or {}
    name     = (body.get("name") or "").strip()
    email    = (body.get("email") or "").strip().lower()
    password = body.get("password") or ""
    role     = body.get("role", "student")

    errors = []
    if not name:               errors.append("name is required")
    if not email:              errors.append("email is required")
    if "@" not in email:       errors.append("email is invalid")
    if len(password) < 6:      errors.append("password must be at least 6 characters")
    if role not in ("student","staff","admin"):
        errors.append("role must be student, staff, or admin")

    if errors:
        return jsonify({"success": False, "errors": errors}), 422

    if User.get_by_email(email):
        return jsonify({"success": False, "error": "Email already registered"}), 409

    user  = User.create(name, email, role, password)
    token = secrets.token_hex(32)
    _sessions[token] = user
    return jsonify({"success": True, "token": token, "user": user}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    body     = request.get_json(silent=True) or {}
    email    = (body.get("email") or "").strip().lower()
    password = body.get("password") or ""

    if not email or not password:
        return jsonify({"success": False, "error": "Email and password are required"}), 422

    user = User.verify_login(email, password)
    if not user:
        return jsonify({"success": False, "error": "Invalid email or password"}), 401

    token = secrets.token_hex(32)
    _sessions[token] = user
    return jsonify({"success": True, "token": token, "user": user}), 200


@auth_bp.route("/logout", methods=["POST"])
def logout():
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        _sessions.pop(auth[7:], None)
    return jsonify({"success": True, "message": "Logged out"}), 200


@auth_bp.route("/me", methods=["GET"])
def me():
    user = get_current_user()
    if not user:
        return jsonify({"success": False, "error": "Not authenticated"}), 401
    return jsonify({"success": True, "user": user}), 200
