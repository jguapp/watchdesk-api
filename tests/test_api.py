import unittest

from watchdesk.app import create_app


class ApiTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.testing = True
        self.client = self.app.test_client()
        self.writer = {"Authorization": "Bearer alpha-writer"}
        self.reader = {"Authorization": "Bearer alpha-reader"}

    def test_health_is_public(self):
        response = self.client.get("/health")
        self.assertEqual(200, response.status_code)
        self.assertEqual({"status": "ok"}, response.json)

    def test_authentication_rejects_missing_or_bad_tokens(self):
        for headers in ({}, {"Authorization": "Basic abc"}, {"Authorization": "Bearer nope"}):
            with self.subTest(headers=headers):
                self.assertEqual(401, self.client.get("/incidents", headers=headers).status_code)

    def test_list_only_returns_own_team(self):
        response = self.client.get("/incidents", headers=self.writer)
        self.assertEqual(["inc_1", "inc_2"], [item["id"] for item in response.json["data"]])

    def test_other_team_and_missing_ids_look_missing(self):
        for incident_id in ("inc_3", "missing"):
            with self.subTest(id=incident_id):
                self.assertEqual(404, self.client.get(f"/incidents/{incident_id}", headers=self.writer).status_code)

    def test_filter_and_invalid_status(self):
        self.assertEqual([], self.client.get("/incidents?status=resolved", headers=self.writer).json["data"])
        self.assertEqual(2, len(self.client.get("/incidents?status=open", headers=self.writer).json["data"]))
        self.assertEqual(400, self.client.get("/incidents?status=nope", headers=self.writer).status_code)

    def test_reader_cannot_create_or_rename(self):
        created = self.client.post("/incidents", headers=self.reader, json={"title": "Down", "service": "api"})
        renamed = self.client.patch("/incidents/inc_1", headers=self.reader, json={"title": "New"})
        self.assertEqual(403, created.status_code)
        self.assertEqual(403, renamed.status_code)

    def test_create_normalizes_saves_and_uses_authenticated_identity(self):
        response = self.client.post("/incidents", headers=self.writer, json={
            "title": "  API down  ", "service": " api ", "created_by": "blair", "team_id": "beta",
        })
        self.assertEqual(201, response.status_code)
        created = response.json["data"]
        self.assertEqual("API down", created["title"])
        self.assertEqual("api", created["service"])
        self.assertEqual("alex", created["created_by"])
        self.assertEqual("open", created["status"])
        self.assertNotIn("team_id", created)
        loaded = self.client.get(response.headers["Location"], headers=self.writer)
        self.assertEqual(created, loaded.json["data"])

    def test_bad_body_and_wrong_content_type(self):
        for body in ([], None, "text"):
            with self.subTest(body=body):
                import json
                response = self.client.post("/incidents", headers=self.writer, data=json.dumps(body), content_type="application/json")
                self.assertEqual(400, response.status_code)
        malformed = self.client.post("/incidents", headers=self.writer, data="{", content_type="application/json")
        self.assertEqual(400, malformed.status_code)
        self.assertEqual(415, self.client.post("/incidents", headers=self.writer, data="text").status_code)

    def test_invalid_fields_do_not_create_incidents(self):
        for title, service in ((" ", "api"), (123, "api"), ("x" * 81, "api"), ("Down", ""), ("Down", "s" * 41)):
            with self.subTest(title=title, service=service):
                response = self.client.post("/incidents", headers=self.writer, json={"title": title, "service": service})
                self.assertEqual(400, response.status_code)
        self.assertEqual(2, len(self.client.get("/incidents", headers=self.writer).json["data"]))

    def test_inclusive_title_boundary(self):
        response = self.client.post("/incidents", headers=self.writer, json={"title": "x" * 80, "service": "api"})
        self.assertEqual(201, response.status_code)

    def test_rename_persists_and_keeps_other_fields(self):
        response = self.client.patch("/incidents/inc_1", headers=self.writer, json={"title": " New title "})
        self.assertEqual(200, response.status_code)
        stored = self.client.get("/incidents/inc_1", headers=self.writer).json["data"]
        self.assertEqual("New title", stored["title"])
        self.assertEqual("checkout", stored["service"])
        self.assertEqual(response.json["data"], stored)

    def test_foreign_rename_does_not_change_other_team(self):
        response = self.client.patch("/incidents/inc_3", headers=self.writer, json={"title": "Changed"})
        self.assertEqual(404, response.status_code)
        foreign = self.client.get("/incidents/inc_3", headers={"Authorization": "Bearer beta-writer"})
        self.assertEqual("Worker is down", foreign.json["data"]["title"])

    def test_wrong_method_preserves_allow_header(self):
        response = self.client.delete("/incidents/inc_1", headers=self.writer)
        self.assertEqual(405, response.status_code)
        self.assertIn("PATCH", response.headers["Allow"])
        self.assertIn("error", response.json)

    def test_new_application_has_fresh_storage(self):
        self.client.patch("/incidents/inc_1", headers=self.writer, json={"title": "Changed"})
        other_client = create_app().test_client()
        self.assertEqual("Checkout is slow", other_client.get("/incidents/inc_1", headers=self.writer).json["data"]["title"])

    def test_request_body_is_bounded(self):
        response = self.client.post("/incidents", headers=self.writer, json={"title": "x" * 20_000})
        self.assertEqual(413, response.status_code)

    def test_resolve_response(self):
        response = self.client.post("/incidents/inc_1/resolve", headers=self.writer,
                                    json={"resolution_note": "  Restarted the service  "})
        self.assertEqual(200, response.status_code)
        self.assertEqual("resolved", response.json["data"]["status"])
        self.assertEqual("Restarted the service", response.json["data"]["resolution_note"])
        self.assertEqual("alex", response.json["data"]["resolved_by"])

    def test_resolve_rejects_blank_note(self):
        response = self.client.post("/incidents/inc_1/resolve", headers=self.writer,
                                    json={"resolution_note": "   "})
        self.assertEqual(400, response.status_code)


if __name__ == "__main__":
    unittest.main()
