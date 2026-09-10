# Final mock: WatchDesk

Start on `main`. Run the tests before the timed interview. Avoid the PR and its
requirements document until your interviewer starts the review phase. Work
without AI assistance for the timed mock. You may search the code, use the
README, and ask the interviewer about unfamiliar Python or Flask syntax.

## Background: 20 minutes

Describe one project you built: the user problem, your contribution, a technical
choice, a bug you investigated, and what you want to learn during an internship.

## Explore: 25 minutes

Trace this request and its response:

```http
PATCH /incidents/inc_1
Authorization: Bearer alpha-writer
Content-Type: application/json

{"title":"  Checkout recovering  "}
```

Explain where the app starts, how the route is selected, how the caller is
identified, how permission and ownership are checked, what is validated, how
the update is saved, and how the result becomes JSON. Then explain what happens
if the caller is `alpha-reader` or the ID is `inc_3`.

Confirm the change by explaining what a later GET would return. You do not
need to read every file or know Flask decorators by memory.

## Design: 20 minutes

The interviewer will introduce a small feature. Talk through its endpoint,
request/response, validations, permissions, data changes, error behavior, and
three useful tests. No implementation is required.

## Review: 20 minutes

Read the written requirements, then the PR diff. For each requirement, decide
whether it is satisfied and cite evidence. For each finding, give an input or
sequence, explain expected versus actual behavior, and suggest a fix or test.
Do not submit or merge anything on GitHub during the mock; take local notes or
describe your comments aloud.

## Debrief: 5 minutes

Summarize the request flow, your main design decision, and the most important
review finding. Reflect on how you used a hint or changed an assumption.

