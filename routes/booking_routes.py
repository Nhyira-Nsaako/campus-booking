from flask import Blueprint
from controllers.booking_controller import BookingController

booking_bp = Blueprint("bookings", __name__, url_prefix="/api/bookings")

booking_bp.add_url_rule("",                  view_func=BookingController.get_all,    methods=["GET"])
booking_bp.add_url_rule("/<int:booking_id>", view_func=BookingController.get_one,    methods=["GET"])
booking_bp.add_url_rule("",                  view_func=BookingController.create,     methods=["POST"])
booking_bp.add_url_rule("/<int:booking_id>", view_func=BookingController.update,     methods=["PUT"])
booking_bp.add_url_rule("/<int:booking_id>", view_func=BookingController.delete,     methods=["DELETE"])
booking_bp.add_url_rule("/<int:booking_id>/hard", view_func=BookingController.hard_delete, methods=["DELETE"])
