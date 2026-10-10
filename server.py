#!/usr/bin/env python3
"""A tiny, local, intentionally-flawed record server for the lab.

It exposes two routes behind a bearer token:

    GET /api/dossiers        -> list the caller's permitted records
    GET /api/dossiers/{id}   -> read one record

The list route filters correctly. The *detail* route is where the deliberate
broken-object-level-authorization (BOLA / IDOR) flaw lives: with --vulnerable it
returns any record to any signed-in caller. The protected default enforces the
check in lab/policy.py.

Loopback only. All data is synthetic. Run:

    python3 server.py --vulnerable     # reproduce the flaw
    python3 server.py                  # protected (default)
"""

import argparse
import json
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

from lab import policy

ROOT = Path(__file__).resolve().parent
FIXTURES = json.loads((ROOT / "lab" / "fixtures.json").read_text())
ACCOUNTS = {a["token"]: a for a in FIXTURES["accounts"]}
DOSSIERS = {d["id"]: d for d in FIXTURES["dossiers"]}


class Handler(BaseHTTPRequestHandler):
    vulnerable = False

    def log_message(self, *args):
        pass

    def account(self):
        auth = self.headers.get("Authorization", "")
        token = auth[7:] if auth.startswith("Bearer ") else ""
        return ACCOUNTS.get(token)

    def reply(self, status, payload):
        body = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = urlsplit(self.path).path
        account = self.account()
        if account is None:
            return self.reply(401, {"error": "Sign in with a valid account token."})

        if path == "/api/dossiers":
            items = [
                {k: d[k] for k in ("id", "title", "workspace")}
                for d in DOSSIERS.values()
                if account["role"] == "operator" or d["workspace"] == account["workspace"]
            ]
            return self.reply(200, {"items": items})

        match = re.fullmatch(r"/api/dossiers/(\d+)", path)
        if match:
            dossier = DOSSIERS.get(int(match.group(1)))
            if dossier is None:
                return self.reply(404, {"error": "No such record in the synthetic lab."})
            if not policy.can_read_dossier(account, dossier, self.vulnerable):
                return self.reply(403, {"error": "Your account may not read this record."})
            return self.reply(200, {"dossier": dossier})

        return self.reply(404, {"error": "That route is not part of this lab."})


def main():
    parser = argparse.ArgumentParser(description="A tiny local BOLA lab. Synthetic data, loopback only.")
    parser.add_argument("--vulnerable", action="store_true", help="Reproduce the deliberate flaw.")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    Handler.vulnerable = args.vulnerable
    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    mode = "VULNERABLE (flaw active)" if args.vulnerable else "protected (default)"
    print("Raid the Watchtower lab — mode: %s" % mode)
    print("http://127.0.0.1:%d/api/dossiers   (Ctrl+C to stop)" % args.port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
