# WatchDesk

A small Python / Flask incident tracker for a final backend mock interview.
Teams can create, list, read, and rename incidents. Start with `main` and follow
one request through the code. The app is intentionally small enough to explore
in 20–25 minutes.

## Run

Requires Python 3.11 or later. From this repository directory:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe -m flask --app watchdesk.app:create_app run --port 8011
```

On macOS/Linux, use `.venv/bin/python` in place of `.\.venv\Scripts\python.exe`.
The server runs at `http://127.0.0.1:8011`. No database server is needed.

```powershell
Invoke-RestMethod http://127.0.0.1:8011/incidents -Headers @{Authorization='Bearer alpha-writer'}
```

## Demo identities

These are public training fixtures, not real secrets.

| Bearer token | User | Team | Access |
| --- | --- | --- | --- |
| `alpha-writer` | `alex` | `alpha` | Read and write |
| `alpha-reader` | `riley` | `alpha` | Read only |
| `beta-writer` | `blair` | `beta` | Read and write |

Seed data: `inc_1` and `inc_2` belong to Alpha; `inc_3` belongs to Beta. A team
cannot read or edit another team's incidents. Missing and foreign IDs return 404.

## Files to explore

| File | Responsibility |
| --- | --- |
| `watchdesk/app.py` | App factory, Flask routes, JSON parsing, error responses |
| `watchdesk/auth.py` | Bearer token lookup, user identity and write permission |
| `watchdesk/service.py` | Validation and use-case logic |
| `watchdesk/repository.py` | Dictionary storage and team-scoped reads |
| `watchdesk/models.py` | Immutable Incident and response serialization |
| `watchdesk/errors.py` | An error carrying an HTTP status |
| `tests/test_api.py` | API-level behavior tests |

The path to follow is: Flask route → service → repository → response.
Authentication runs in `before_request` for matched protected endpoints.

## Current API

| Method | URL | Body | Success |
| --- | --- | --- | --- |
| GET | `/health` | None; no token needed | 200, `{"status":"ok"}` |
| GET | `/incidents?status=open` | None; optional open/resolved filter | 200, `{"data":[...]}` |
| GET | `/incidents/<incident_id>` | None | 200, `{"data":{...}}` |
| POST | `/incidents` | `{"title":"API down","service":"api"}` | 201 with Location header |
| PATCH | `/incidents/<incident_id>` | `{"title":"API recovering"}` | 200 with saved incident |

Writes require `Content-Type: application/json`. Titles are trimmed and must
contain 1–80 characters; service names contain 1–40. Unknown body fields are
ignored. Identity and team ownership come from the token.

Example `GET /incidents/inc_1` response:

```json
{
  "data": {
    "id": "inc_1",
    "title": "Checkout is slow",
    "service": "checkout",
    "created_by": "alex",
    "status": "open",
    "resolution_note": null,
    "resolved_by": null
  }
}
```

Error envelope: `{"error":"Incident not found"}`. Common statuses are 400 for
invalid input, 401 for a bad/missing token, 403 for missing write permission,
404 for missing/foreign resources, 405 for a wrong method, 413 for a body over
16 KiB, and 415 for a non-JSON write body.

## Mock instructions

Read [CANDIDATE.md](CANDIDATE.md). Your interviewer will introduce the feature
design and provide the PR when you reach the review phase. Use the PR's Files
changed tab to compare the final change with its written acceptance criteria.

## Scope

Storage resets when the process restarts. This teaching app intentionally omits
database persistence, pagination, production identity, and concurrent-update
protection. Mention those as future work if asked; focus the mock on the current
contract. This is an original practice exercise based on the interview format
you supplied, not an official Datadog question or scoring rubric.

Flask references: [routes and JSON](https://flask.palletsprojects.com/en/stable/quickstart/),
[test client](https://flask.palletsprojects.com/en/stable/testing/).

