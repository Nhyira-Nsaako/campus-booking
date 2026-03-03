from flask import request, jsonify
from models.booking import Booking
from models.facility import Facility
from datetime import datetime, timedelta

OPENING_HOUR = 7    # 07:00
CLOSING_HOUR = 22   # 22:00
SLOT_MINUTES = 30

def _generate_slots(date, booked):
    """Generate all 30-minute slots for the day and mark availability."""
    slots = []
    start = datetime.strptime(f"{date} {OPENING_HOUR:02d}:00", "%Y-%m-%d %H:%M")
    end   = datetime.strptime(f"{date} {CLOSING_HOUR:02d}:00", "%Y-%m-%d %H:%M")
    current = start

    while current < end:
        slot_start = current.strftime("%H:%M")
        slot_end   = (current + timedelta(minutes=SLOT_MINUTES)).strftime("%H:%M")

        is_booked = any(
            b["start_time"] <= slot_start < b["end_time"]
            for b in booked
        )

        slots.append({
            "start_time": slot_start,
            "end_time":   slot_end,
            "available":  not is_booked
        })
        current += timedelta(minutes=SLOT_MINUTES)

    return slots


class AvailabilityController:
    """Controller – returns 30-minute slot availability for a facility."""

    @staticmethod
    def check():
        facility_id = request.args.get("facility_id", type=int)
        date        = request.args.get("date", "")

        errors = []
        if not facility_id:
            errors.append("facility_id query param is required (integer)")
        if not date:
            errors.append("date query param is required (YYYY-MM-DD)")
        else:
            try:
                datetime.strptime(date, "%Y-%m-%d")
            except ValueError:
                errors.append("date must be in YYYY-MM-DD format")

        if errors:
            return jsonify({"success": False, "errors": errors}), 422

        facility = Facility.get_by_id(facility_id)
        if not facility:
            return jsonify({"success": False, "error": "Facility not found"}), 404

        booked = Booking.get_booked_slots(facility_id, date)
        slots  = _generate_slots(date, booked)

        available_count = sum(1 for s in slots if s["available"])

        return jsonify({
            "success":  True,
            "facility": facility,
            "date":     date,
            "slots":    slots,
            "summary": {
                "total":     len(slots),
                "available": available_count,
                "booked":    len(slots) - available_count
            }
        }), 200
