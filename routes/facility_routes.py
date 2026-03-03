from flask import Blueprint
from controllers.facility_controller import FacilityController

facility_bp = Blueprint("facilities", __name__, url_prefix="/api/facilities")

facility_bp.add_url_rule("",          view_func=FacilityController.get_all,  methods=["GET"])
facility_bp.add_url_rule("/<int:facility_id>", view_func=FacilityController.get_one, methods=["GET"])
facility_bp.add_url_rule("",          view_func=FacilityController.create,   methods=["POST"])
facility_bp.add_url_rule("/<int:facility_id>", view_func=FacilityController.update,  methods=["PUT"])
facility_bp.add_url_rule("/<int:facility_id>", view_func=FacilityController.delete,  methods=["DELETE"])
