from flask import request, jsonify
from models.facility import Facility

class FacilityController:
    """Controller – validates input, calls Model, returns JSON responses."""

    @staticmethod
    def get_all():
        facilities = Facility.get_all()
        return jsonify({"success": True, "data": facilities, "count": len(facilities)}), 200

    @staticmethod
    def get_one(facility_id):
        facility = Facility.get_by_id(facility_id)
        if not facility:
            return jsonify({"success": False, "error": "Facility not found"}), 404
        return jsonify({"success": True, "data": facility}), 200

    @staticmethod
    def create():
        body = request.get_json(silent=True) or {}
        name     = body.get("name", "").strip()
        location = body.get("location", "").strip()
        capacity = body.get("capacity")

        errors = []
        if not name:
            errors.append("name is required")
        if not location:
            errors.append("location is required")
        if capacity is None:
            errors.append("capacity is required")
        elif not isinstance(capacity, int) or capacity <= 0:
            errors.append("capacity must be a positive integer")

        if errors:
            return jsonify({"success": False, "errors": errors}), 422

        facility = Facility.create(name, location, int(capacity))
        return jsonify({"success": True, "data": facility}), 201

    @staticmethod
    def update(facility_id):
        if not Facility.get_by_id(facility_id):
            return jsonify({"success": False, "error": "Facility not found"}), 404

        body     = request.get_json(silent=True) or {}
        name     = body.get("name", "").strip()
        location = body.get("location", "").strip()
        capacity = body.get("capacity")

        errors = []
        if not name:     errors.append("name is required")
        if not location: errors.append("location is required")
        if capacity is None:
            errors.append("capacity is required")
        elif not isinstance(capacity, int) or capacity <= 0:
            errors.append("capacity must be a positive integer")

        if errors:
            return jsonify({"success": False, "errors": errors}), 422

        facility = Facility.update(facility_id, name, location, int(capacity))
        return jsonify({"success": True, "data": facility}), 200

    @staticmethod
    def delete(facility_id):
        if not Facility.get_by_id(facility_id):
            return jsonify({"success": False, "error": "Facility not found"}), 404
        Facility.delete(facility_id)
        return jsonify({"success": True, "message": "Facility deleted"}), 200
