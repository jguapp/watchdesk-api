from dataclasses import dataclass

from .errors import ApiError


@dataclass(frozen=True)
class User:
    id: str
    team_id: str
    can_write: bool

    def require_writer(self):
        if not self.can_write:
            raise ApiError(403, "Write permission is required")


# Public demo credentials for the mock, not real secrets.
DEMO_TOKENS = {
    "alpha-writer": User("alex", "alpha", True),
    "alpha-reader": User("riley", "alpha", False),
    "beta-writer": User("blair", "beta", True),
}


def authenticate(header: str | None) -> User:
    if not header or not header.startswith("Bearer "):
        raise ApiError(401, "A bearer token is required")
    user = DEMO_TOKENS.get(header.removeprefix("Bearer ").strip())
    if user is None:
        raise ApiError(401, "Invalid bearer token")
    return user

