# The lab: one real, runnable flaw

This is the project's single live demo: a tiny HTTP server with a genuine
broken-object-level-authorization (BOLA / IDOR) flaw. No dependencies, standard
library only, loopback only, all data synthetic.

## Run it

From the repository root:

```bash
# Protected build (default). The fix is active.
python3 server.py
# -> http://127.0.0.1:8765/api/dossiers

# Vulnerable build. The deliberate flaw is active.
python3 server.py --vulnerable
```

Two synthetic accounts (bearer tokens):

- `analyst-demo-token` is scoped to the `demo` workspace (records 101 and 102).
- `operator-demo-token` is an operator who may review every workspace.

## See the flaw, then the fix

```bash
# Start vulnerable, in one terminal:
python3 server.py --vulnerable

# In another terminal, request a record OUTSIDE the analyst's workspace:
curl -s -H "Authorization: Bearer analyst-demo-token" \
  http://127.0.0.1:8765/api/dossiers/103
# Vulnerable: 200 OK plus the restricted record. The leak.

# Stop it, start the protected default, repeat the same request:
python3 server.py
curl -s -o /dev/null -w "%{http_code}\n" \
  -H "Authorization: Bearer analyst-demo-token" \
  http://127.0.0.1:8765/api/dossiers/103
# Protected: 403. Own records 101 and 102 still return 200.
```

## Tests

```bash
python3 -m unittest discover -s tests
```

Seven checks: the flaw leaks in vulnerable mode, is blocked in protected mode,
own-record and operator access are preserved, the list stays filtered, a missing
token is rejected and a missing record is `404` (not `403`).

## Files

- [`../server.py`](../server.py) is the server and its two routes.
- [`policy.py`](policy.py) is `can_read_dossier`, the one authorization decision.
- [`fixtures.json`](fixtures.json) holds the synthetic accounts and records.
- [`../tests/test_lab.py`](../tests/test_lab.py) holds the checks.

The full attack-and-defence write-up is
[`../dossiers/01-broken-access-control.md`](../dossiers/01-broken-access-control.md).
