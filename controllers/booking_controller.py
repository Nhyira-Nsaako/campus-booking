from flask import request, jsonify
from models.booking import Booking
from models.facility import Facility
from models.user import User
import re

TIME_RE = re.compile(r"^\d{2}:\d{2}$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
VALID_STATUS = {"confirmed", "cancelled", "pending"}

def _validate_time_order(start, end):
    return start < end

class BookingController:
    """Controller – validates input, handles conflict logic, returns responses."""

    @staticmethod
    def get_all():
        bookings = Booking.get_all()
        return jsonify({"success": True, "data": bookings, "count": len(bookings)}), 200

    @staticmethod
    def get_one(booking_id):
        booking = Booking.get_by_id(booking_id)
        if not booking:
            return jsonify({"success": False, "error": "Booking not found"}), 404
        return jsonify({"success": True, "data": booking}), 200

    @staticmethod
    def create():
        body = request.get_json(silent=True) or {}
        facility_id = body.get("facility_id")
        user_id     = body.get("user_id")
        date        = body.get("date", "")
        start_time  = body.get("start_time", "")
        end_time    = body.get("end_time", "")
        status      = body.get("status", "confirmed")

        errors = []
        if not facility_id: errors.append("facility_id is required")
        if not user_id:     errors.append("user_id is required")
        if not DATE_RE.match(date): errors.append("date must be YYYY-MM-DD")
        if not TIME_RE.match(start_time): errors.append("start_time must be HH:MM")
        if not TIME_RE.match(end_time):   errors.append("end_time must be HH:MM")
        if status not in VALID_STATUS:    errors.append(f"status must be one of {VALID_STATUS}")

        if errors:
            return jsonify({"success": False, "errors": errors}), 422

        # Round times to nearest 30-minute slot
        def round_30(t):
            h, m = map(int, t.split(":"))
            m = 0 if m < 30 else 30
            return f"{h:02d}:{m:02d}"

        start_time = round_30(start_time)
        end_time   = round_30(end_time)

        if not _validate_time_order(start_time, end_time):
            return jsonify({"success": False, "error": "end_time must be after start_time"}), 422

        if not Facility.get_by_id(facility_id):
            return jsonify({"success": False, "error": "Facility not found"}), 404
        if not User.get_by_id(user_id):
            return jsonify({"success": False, "error": "User not found"}), 404

        conflicts = Booking.get_conflicts(facility_id, date, start_time, end_time)
        if conflicts:
            return jsonify({
                "success": False,
                "error": "Time slot conflicts with an existing booking",
                "conflicts": conflicts
            }), 409

        booking = Booking.create(facility_id, user_id, date, start_time, end_time, status)
        return jsonify({"success": True, "data": booking}), 201

    @staticmethod
    def update(booking_id):
        existing = Booking.get_by_id(booking_id)
        if not existing:
            return jsonify({"success": False, "error": "Booking not found"}), 404

        body       = request.get_json(silent=True) or {}
        facility_id = body.get("facility_id", existing["facility_id"])
        user_id     = body.get("user_id",     existing["user_id"])
        date        = body.get("date",        existing["date"])
        start_time  = body.get("start_time",  existing["start_time"])
        end_time    = body.get("end_time",    existing["end_time"])
        status      = body.get("status",      existing["status"])

        errors = []
        if not DATE_RE.match(date):       errors.append("date must be YYYY-MM-DD")
        if not TIME_RE.match(start_time): errors.append("start_time must be HH:MM")
        if not TIME_RE.match(end_time):   errors.append("end_time must be HH:MM")
        if status not in VALID_STATUS:    errors.append(f"status must be one of {VALID_STATUS}")
        if errors:
            return jsonify({"success": False, "errors": errors}), 422

        if not _validate_time_order(start_time, end_time):
            return jsonify({"success": False, "error": "end_time must be after start_time"}), 422

        if status != "cancelled":
            conflicts = Booking.get_conflicts(facility_id, date, start_time, end_time, exclude_id=booking_id)
            if conflicts:
                return jsonify({
                    "success": False,
                    "error": "Time slot conflicts with an existing booking",
                    "conflicts": conflicts
                }), 409

        booking = Booking.update(
            booking_id,
            facility_id=facility_id,
            user_id=user_id,
            date=date,
            start_time=start_time,
            end_time=end_time,
            status=status
        )
        return jsonify({"success": True, "data": booking}), 200

    @staticmethod
    def delete(booking_id):
        """Soft delete: marks booking as cancelled (use hard_delete for removal)."""
        if not Booking.get_by_id(booking_id):
            return jsonify({"success": False, "error": "Booking not found"}), 404
        booking = Booking.cancel(booking_id)
        return jsonify({"success": True, "data": booking, "message": "Booking cancelled"}), 200

    @staticmethod
    def hard_delete(booking_id):
        """Permanently removes the booking record."""
        if not Booking.get_by_id(booking_id):
            return jsonify({"success": False, "error": "Booking not found"}), 404
        Booking.delete(booking_id)
        return jsonify({"success": True, "message": "Booking permanently deleted"}), 200
