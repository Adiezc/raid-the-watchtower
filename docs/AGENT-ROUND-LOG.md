# Agent round log

## Exercise status

The participant investigation and red/blue exercise have not started. No exercise findings, repairs or outcomes are claimed here.

## Development assistance

Codex coordinated separate planning, backend, browser-interface and beginner-documentation tasks. These development tasks are not red-team discovery or an independent security assessment. They are kept separate from the live exercise below.

## Participant checkpoint

Initial observations and hypothesis: Not yet recorded.

## Live exercise

The coordinator will append the actual specialist role, model if available, prompt, local target, start/end time, hypothesis or proposal, exact request/response evidence, source patch reference, verification and failures. Only real executed work will be added.

### Red scout

Not started.

### Red validator

Not started.

### Blue defender

Not started.

### Red retest

Not started.

---

## Blue defence round — recorded 2026-10-10 16:51 CEST

Executed by the coordinator against the local lab only (127.0.0.1). All records are fictional. This is a controlled test of one known flaw and its repair, not an open-ended attack tool.

### Finding (broken object-level authorisation / IDOR)

The dossier-read endpoint authenticated the caller but never checked ownership, so any signed-in account could open every restricted file.

Evidence, vulnerable build (`--training-vulnerable`, port 8765), analyst token:
- `GET /api/dossiers/103` -> **HTTP 200** (restricted NextVoice file leaked)
- `GET /api/dossiers/104` -> **HTTP 200** (restricted NextVoice file leaked)

### Repair

`lab/policy.can_read_dossier` now authorises by workspace and role instead of by authentication alone: a caller may read a dossier only when the dossier's workspace matches the caller's, or the caller is an operator. The deliberate flaw is reachable only under the explicit `--training-vulnerable` flag; the protected build is the default. `PROTECTED_IMPLEMENTED` is now `True` and the obsolete pre-repair startup guard was removed.

### Retest, protected build (default, port 8766), same analyst token

| Request | Result | Meaning |
| --- | --- | --- |
| `GET /api/dossiers/101` | HTTP 200 | own workspace, still allowed |
| `GET /api/dossiers/102` | HTTP 200 | own workspace, still allowed |
| `GET /api/dossiers/103` | HTTP 403 | restricted file now blocked |
| `GET /api/dossiers/104` | HTTP 403 | restricted file now blocked |
| `GET /api/dossiers/105` | HTTP 403 | unrelated restricted file blocked |
| `GET /api/dossiers/106` | HTTP 403 | unrelated restricted file blocked |
| `GET /api/dossiers/999` | HTTP 404 | missing file still 404, no 403/404 oracle change |
| `GET /api/dossiers/103` as operator | HTTP 200 | legitimate operator review preserved |

403 body: `{"error": "Your account does not have permission to read this file."}`

### Verification
- Automated suite: 13 tests pass (10 baseline + 3 new protected-mode checks). Baseline flaw-present tests and protected-boundary tests both green.
- Runtime source hash at repair time: `a28184a7f58dfb7d…`.
- Still outstanding for the full mission: the participant's recorded first thoughts, the saved restricted-dossier evidence from the investigation, and the live collector-revocation retest with the operator.
