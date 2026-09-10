from .models import Incident


class IncidentRepository:
    """Process-local storage; starting a new application resets the demo data."""

    def __init__(self, incidents=()):
        self._incidents = {item.id: item for item in incidents}

    def get(self, team_id: str, incident_id: str) -> Incident | None:
        incident = self._incidents.get(incident_id)
        if incident is None or incident.team_id != team_id:
            return None
        return incident

    def list(self, team_id: str):
        return sorted(
            (item for item in self._incidents.values() if item.team_id == team_id),
            key=lambda item: item.id,
        )

    def save(self, incident: Incident):
        self._incidents[incident.id] = incident

