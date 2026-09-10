from flask import Flask, g, request
from werkzeug.exceptions import HTTPException

from .auth import authenticate
from .errors import ApiError
from .models import Incident
from .repository import IncidentRepository
from .service import IncidentService


def read_body():
    data = request.get_json()
    if not isinstance(data, dict):
        raise ApiError(400, "Body must be a JSON object")
    return data


def create_app():
    app = Flask(__name__)
    app.config["MAX_CONTENT_LENGTH"] = 16_384
    repository = IncidentRepository([
        Incident("inc_1", "alpha", "Checkout is slow", "checkout", "alex"),
        Incident("inc_2", "alpha", "Search errors", "search", "alex"),
        Incident("inc_3", "beta", "Worker is down", "worker", "blair"),
    ])
    service = IncidentService(repository)
    app.extensions["incident_service"] = service

    @app.before_request
    def identify_user():
        # Let Flask produce its own 404/405 for unmatched routes.
        if request.endpoint is not None and request.endpoint != "health":
            g.user = authenticate(request.headers.get("Authorization"))

    @app.errorhandler(ApiError)
    def handle_domain_error(error):
        return {"error": str(error)}, error.status

    @app.errorhandler(HTTPException)
    def handle_http_error(error):
        # Keep protocol headers such as Allow on Flask's error response.
        response = error.get_response()
        response.data = app.json.dumps({"error": error.description})
        response.content_type = "application/json"
        return response

    @app.get("/health")
    def health():
        return {"status": "ok"}

    @app.get("/incidents")
    def list_incidents():
        items = service.list(g.user, request.args.get("status"))
        return {"data": [item.to_dict() for item in items]}

    @app.get("/incidents/<incident_id>")
    def get_incident(incident_id):
        return {"data": service.get(g.user, incident_id).to_dict()}

    @app.post("/incidents")
    def create_incident():
        incident = service.create(g.user, read_body())
        return {"data": incident.to_dict()}, 201, {"Location": f"/incidents/{incident.id}"}

    @app.patch("/incidents/<incident_id>")
    def rename_incident(incident_id):
        return {"data": service.rename(g.user, incident_id, read_body()).to_dict()}

    return app

