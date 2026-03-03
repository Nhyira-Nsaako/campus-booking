"""
Campus Facility Booking System
CPEN 412 – Web Software Architecture
MVC Architecture: Flask (Controller+Routes) + SQLite (Model) + HTML/JS (View)
"""

from flask import Flask, send_from_directory, jsonify, request
from config.database import init_db
from routes.facility_routes     import facility_bp
from routes.booking_routes      import booking_bp
from routes.availability_routes import availability_bp
from routes.user_routes         import user_bp
from routes.auth_routes         import auth_bp
import os

app = Flask(__name__, static_folder="public", static_url_path="")

@app.after_request
def add_cors(response):
    response.headers["Access-Control-Allow-Origin"]  = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET,POST,PUT,DELETE,OPTIONS"
    return response

@app.before_request
def handle_options():
    if request.method == "OPTIONS":
        return jsonify({}), 200

app.register_blueprint(facility_bp)
app.register_blueprint(booking_bp)
app.register_blueprint(availability_bp)
app.register_blueprint(user_bp)
app.register_blueprint(auth_bp)

@app.route("/api/health")
def health():
    return jsonify({"status": "ok", "service": "Campus Facility Booking API", "version": "2.0.0"}), 200

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve(path):
    if path and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    return send_from_directory(app.static_folder, "index.html")

@app.errorhandler(404)
def not_found(e):
    return jsonify({"success": False, "error": "Endpoint not found"}), 404

@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({"success": False, "error": "Method not allowed"}), 405

@app.errorhandler(500)
def server_error(e):
    return jsonify({"success": False, "error": "Internal server error"}), 500

init_db()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"\n🏛  Campus Facility Booking System v2 running on http://localhost:{port}\n")
    app.run(host="0.0.0.0", port=port, debug=True)
