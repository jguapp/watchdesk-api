# Feature: resolve an incident with a note

Read when the interviewer starts the review phase. These are the acceptance
criteria for the proposed PR; they are the source of truth for this exercise.

Add `POST /incidents/<incident_id>/resolve`.

```http
POST /incidents/inc_1/resolve
Authorization: Bearer alpha-writer
Content-Type: application/json

{"resolution_note":"  Restarted the service  "}
```

Expected response: 200, the same `{"data": incident}` envelope used by GET.
The returned incident keeps its ID, title, service, and creator, and has:

```json
{
  "status": "resolved",
  "resolution_note": "Restarted the service",
  "resolved_by": "alex"
}
```

| ID | Acceptance criterion |
| --- | --- |
| R1 | A valid writer token is required. Missing/invalid token → 401; reader → 403. |
| R2 | Load the incident within the authenticated user's team. Missing or foreign incident → 404, no change. |
| R3 | `resolution_note` must be a string. Trim surrounding whitespace, then require **1–200 characters inclusive**. Missing, blank, non-string, or over 200 → 400 with no change. |
| R4 | `resolved_by` must come from the authenticated user. Ignore any body-supplied `resolved_by` or team identity. |
| R5 | Success → 200 and the complete incident with status `resolved`, trimmed note, and actor. Preserve ID, title, service, and creator. |
| R6 | Save the updated incident. A subsequent GET must show the same result; the incident must disappear from `?status=open` and appear in `?status=resolved`. |
| R7 | An incident already stored as `resolved` → 409 without replacing its original note or resolver. |
| R8 | Reuse the existing JSON parsing/error envelope. Invalid JSON or a non-object JSON body → 400; non-JSON content type → 415. |

For grading, R5 concerns the response shape/state and preserved fields; the
actor's source is scored under R4 and later storage reads under R6.

In scope: one route, a service method, and tests. No notification worker,
database migration, Flask rewrite, or production deployment is required.
Assume sequential requests in one running process. Existing in-memory storage
and authentication fixtures remain appropriate for this exercise.

Before approving, use a different note from the sample, try the documented
boundaries, and consider whether checking only the POST response proves R6.
