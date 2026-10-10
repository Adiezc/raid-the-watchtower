"""Checks for the BOLA lab: the flaw is real in vulnerable mode and closed in
protected mode, and legitimate access is preserved either way."""

import json
import threading
import unittest
from http.server import ThreadingHTTPServer
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import server

ANALYST = "analyst-demo-token"
OPERATOR = "operator-demo-token"


class LabCase(unittest.TestCase):
    def serve(self, vulnerable):
        server.Handler.vulnerable = vulnerable
        httpd = ThreadingHTTPServer(("127.0.0.1", 0), server.Handler)
        threading.Thread(target=httpd.serve_forever, daemon=True).start()
        self.addCleanup(httpd.server_close)
        self.addCleanup(httpd.shutdown)
        return "http://127.0.0.1:%d" % httpd.server_port

    def get(self, base, path, token=ANALYST):
        headers = {"Authorization": "Bearer " + token} if token else {}
        try:
            with urlopen(Request(base + path, headers=headers)) as r:
                return r.status, json.loads(r.read())
        except HTTPError as e:
            return e.code, json.loads(e.read())

    def test_vulnerable_leaks_restricted_record(self):
        base = self.serve(vulnerable=True)
        status, body = self.get(base, "/api/dossiers/103")
        self.assertEqual(status, 200)
        self.assertEqual(body["dossier"]["id"], 103)

    def test_protected_blocks_restricted_record(self):
        base = self.serve(vulnerable=False)
        self.assertEqual(self.get(base, "/api/dossiers/103")[0], 403)
        self.assertEqual(self.get(base, "/api/dossiers/104")[0], 403)

    def test_protected_allows_own_record(self):
        base = self.serve(vulnerable=False)
        status, body = self.get(base, "/api/dossiers/101")
        self.assertEqual(status, 200)
        self.assertEqual(body["dossier"]["id"], 101)

    def test_list_is_filtered_to_own_workspace(self):
        base = self.serve(vulnerable=False)
        status, body = self.get(base, "/api/dossiers")
        self.assertEqual(status, 200)
        self.assertEqual({d["id"] for d in body["items"]}, {101, 102})

    def test_operator_may_review_every_workspace(self):
        base = self.serve(vulnerable=False)
        self.assertEqual(self.get(base, "/api/dossiers/103", token=OPERATOR)[0], 200)

    def test_missing_token_is_rejected(self):
        base = self.serve(vulnerable=False)
        self.assertEqual(self.get(base, "/api/dossiers/101", token=None)[0], 401)

    def test_missing_record_is_404_not_403(self):
        base = self.serve(vulnerable=False)
        self.assertEqual(self.get(base, "/api/dossiers/999")[0], 404)


if __name__ == "__main__":
    unittest.main()
