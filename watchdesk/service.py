from dataclasses import replace
from uuid import uuid4

from .auth import User
from .errors import ApiError
from .models import Incident
from .repository import IncidentRepository


def required_text(value, field, maximum):
    if not isinstance(value, str) or not value.strip():
        raise ApiError(400, f"{field} must be non-empty text")
    text = value.strip()
    if len(text) > maximum:
        raise ApiError(400, f"{field} must be at most {maximum} characters")
    return text


class IncidentService:
    def __init__(self, repository: IncidentRepository):
        self.repository = repository

    def get(self, user: User, incident_id: str):
        incident = self.repository.get(user.team_id, incident_id)
        if incident is None:
            raise ApiError(404, "Incident not found")
        return incident

    def list(self, user: User, status=None):
        if status is not None and status not in ("open", "resolved"):
            raise ApiError(400, "status must be open or resolved")
        incidents = self.repository.list(user.team_id)
        return [item for item in incidents if status is None or item.status == status]

    def create(self, user: User, data: dict):
        user.require_writer()
        title = required_text(data.get("title"), "title", 80)
        service = required_text(data.get("service"), "service", 40)
        incident = Incident(
            id=f"inc_{uuid4().hex}",
            team_id=user.team_id,
            title=title,
            service=service,
            created_by=user.id,
        )
        self.repository.save(incident)
        return incident

    def rename(self, user: User, incident_id: str, data: dict):
        user.require_writer()
        current = self.get(user, incident_id)
        title = required_text(data.get("title"), "title", 80)
        updated = replace(current, title=title)
        self.repository.save(updated)
        return updated

