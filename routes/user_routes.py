from flask import Blueprint, jsonify, request
from models.user import User

user_bp = Blueprint("users", __name__, url_prefix="/api/users")

@user_bp.route("", methods=["GET"])
def get_all():
    users = User.get_all()
    return jsonify({"success": True, "data": users, "count": len(users)}), 200

@user_bp.route("/<int:user_id>", methods=["GET"])
def get_one(user_id):
    user = User.get_by_id(user_id)
    if not user:
        return jsonify({"success": False, "error": "User not found"}), 404
    return jsonify({"success": True, "data": user}), 200

@user_bp.route("", methods=["POST"])
def create():
    body  = request.get_json(silent=True) or {}
    name  = body.get("name", "").strip()
    email = body.get("email", "").strip()
    role  = body.get("role", "student")
    errors = []
    if not name:  errors.append("name is required")
    if not email: errors.append("email is required")
    if role not in ("student","staff","admin"):
        errors.append("role must be student, staff, or admin")
    if errors:
        return jsonify({"success": False, "errors": errors}), 422
    if User.get_by_email(email):
        return jsonify({"success": False, "error": "Email already registered"}), 409
    user = User.create(name, email, role)
    return jsonify({"success": True, "data": user}), 201
