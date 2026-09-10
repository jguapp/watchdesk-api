from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class Incident:
    id: str
    team_id: str
    title: str
    service: str
    created_by: str
    status: str = "open"
    resolution_note: str | None = None
    resolved_by: str | None = None

    def to_dict(self):
        data = asdict(self)
        data.pop("team_id")
        return data

