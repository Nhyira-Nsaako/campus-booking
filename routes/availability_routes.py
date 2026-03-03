from flask import Blueprint
from controllers.availability_controller import AvailabilityController

availability_bp = Blueprint("availability", __name__, url_prefix="/api/availability")

availability_bp.add_url_rule("", view_func=AvailabilityController.check, methods=["GET"])
