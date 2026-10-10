# Agent round log

## Exercise status

A full guided playthrough and a bounded red/blue agent round were executed on
2026-10-10 evening (CEST) at Adrian's request that Claude "go through it as if you
were a user and check everything". This is a recorded Claude-run exercise, not
Adrian's own participation and not a live autonomous production swarm. Run
`run-9f4b3eb9ce20`, local target `127.0.0.1:8765`. The results below are real
executed work with exact request/response evidence. The mission reached the
intended **Victory With Loose Ends** ending, confirmed by the actual server.

## Development assistance

Codex coordinated separate planning, backend, browser-interface and beginner-documentation tasks. These development tasks are not red-team discovery or an independent security assessment. They are kept separate from the live exercise below.

## Participant checkpoint

Recorded **before** any exploit was run and before any agent conclusion was seen
(saved in the browser notebook ~21:46 CEST on 2026-10-10, run `run-9f4b3eb9ce20`).
Full text in [INVESTIGATION-NOTES.md](INVESTIGATION-NOTES.md).

- Observation: Rowan's private raid-night joke ("unionising the dragons") appears
  word-for-word on Gallantir's CivicLens slide, labelled CL-103; the channel is
  private, so a verbatim quote should not be reachable from outside the guild.
- Hypothesis: something forwards the guild's private messages into CivicLens
  (probably the raid companion add-on); CL-103 likely maps to internal record
  103; and the platform may hand restricted records to any signed-in account —
  to be tested by requesting record 103, which is not in the permitted list
  (101, 102).

## Live exercise

Coordinator: this Claude session. Red and blue roles were run as separate
bounded subagents (general-purpose Claude agents with shell access), each given a
self-contained prompt, strict loopback-only scope, and the synthetic analyst
token. The two red agents were not shown each other's conclusions. All data is
fictional. This is a recorded exercise, not live autonomous activity.

### Red scout — 2026-10-10 ~21:40 CEST

- Target: `http://127.0.0.1:8765` only, read-only curl. Credential: analyst token.
- Hypothesis (stated before confirming): the analyst token is validated for
  authentication but the detail endpoint `GET /api/dossiers/{id}` does not enforce
  authorisation against `allowed_dossier_ids` — classic IDOR / BOLA.
- Requests and results (all with the analyst token):
  - `GET /api/session` → 200 (allowed ids = 101, 102; mode training-vulnerable)
  - `GET /api/dossiers` → 200 (list shows only 101, 102 / workspace demo)
  - `GET /api/brief` → 200 (slide quote tied to `source_ref: CL-103`)
  - `GET /api/dossiers/100` → 404 (no such record — boundary behaves normally)
  - `GET /api/dossiers/101` → 200 (in-list, demo)
  - `GET /api/dossiers/102` → 200 (in-list, demo)
  - `GET /api/dossiers/103` → **200 LEAK** (workspace `restricted-nextvoice`)
  - `GET /api/dossiers/104` → **200 LEAK** (`restricted-nextvoice`)
  - `GET /api/dossiers/105` → **200 LEAK** (`restricted-supplier`)
  - `GET /api/dossiers/106` → **200 LEAK** (`restricted-operations`)
- Finding: BOLA / IDOR (OWASP API1). The analyst read records in workspaces it
  has no entitlement to. Record 103 names the collection route: the
  `integration-raid-companion` integration forwarded the private guild message
  into CivicLens, surfacing as slide CL-103. The 404 on id 100 shows the endpoint
  distinguishes missing records but performs no ownership check on records that
  exist.
- Establishes: any holder of the analyst token can read any existing dossier by
  id regardless of workspace; the access decision is absent at the detail
  endpoint while correctly applied at the list endpoint. Does NOT establish write/
  delete capability (only GETs tested) or unauthenticated access (every request
  carried the token). Makes no claim about any real organisation.

### Red validator — 2026-10-10 ~21:40 CEST (independent)

- Target and credential identical; worked without sight of the scout's report.
- Method: read `/api/session` and `/api/dossiers`, then probed detail ids 101–106.
- Result table (analyst token):

  | id | HTTP | workspace | permitted? |
  | --- | --- | --- | --- |
  | 101 | 200 | demo | yes |
  | 102 | 200 | demo | yes |
  | 103 | 200 | restricted-nextvoice | no |
  | 104 | 200 | restricted-nextvoice | no |
  | 105 | 200 | restricted-supplier | no |
  | 106 | 200 | restricted-operations | no |

- Independent verdict: BOLA/IDOR on `GET /api/dossiers/{id}`; **four** restricted
  records across **three** workspaces reachable, i.e. a systematic missing
  authorisation check, not one misconfigured record. The list-vs-detail
  inconsistency is the tell: the server knows the analyst's scope (it filters the
  list) but fails to apply it on detail reads.
- Cannot conclude from loopback alone: other tokens/roles, non-GET exposure, the
  full id space, or behaviour behind a real gateway. Did not inspect source, so it
  pointed only to external behaviour. Data synthetic — no real-world sensitivity.

Both red agents converged independently on the same class and the same primary
ids, which cross-validates the finding. The coordinator's own manual probe (via
API and the browser's numbered record field) matched: `GET /api/dossiers/103`
→ 200 in the vulnerable build, saved as `restricted-dossier` evidence.

### Blue defender — 2026-10-10 ~21:50 CEST (read-only source review)

- Reviewed `lab/policy.py` (`can_read_dossier`) and the `server.py` list and
  detail handlers; confirmed the data model from `fixtures/story.json`. No files
  modified.
- Verdict: the repair (commit `5546f6e`) is **sound and complete** for this flaw.
  - Rule now enforced: deny if no account/dossier; otherwise allow only if the
    caller is an operator, or the dossier's workspace equals the caller's own.
    Authentication alone is no longer sufficient. The analyst (workspace demo) is
    refused all of 103–106 — not just the headline 103.
  - Legitimate access preserved: analyst reads of 101/102 still 200; the operator
    role short-circuit preserves cross-workspace review.
  - Server-side only: account comes from the bearer token → DB; dossier from the
    DB by id; the decision reads only server-held role/workspace. The browser
    supplies only the numeric id (constrained by `re.fullmatch`), which selects
    which record loads but cannot forge a workspace or role. No trust-the-client
    mistake. The `training_vulnerable` bypass is a launch-time CLI flag, fail-closed
    by default.
  - Residual (recorded honestly): a forbidden-but-existing record returns 403
    while a missing record returns 404, so the status code is an **existence
    oracle** — a caller can tell which ids exist. The body leaks no content
    (verify asserts `'dossier' not in response`). Impact is negligible in this
    fixed 101–106 lab. Optional hardening: return 404 for forbidden records too,
    so the detail endpoint reveals nothing about restricted ids' existence.
  - Other notes: list endpoint applies the same filter (parity restored); evidence
    export only preserves the caller's own logged requests (no exfiltration path);
    forbidden reads are logged with actor and mode (supports detection).

### Defence and red retest — protected build, same run `run-9f4b3eb9ce20`

The lab was restarted into the default protected build on the **same database**,
so the participant evidence (clue + restricted-dossier response) persisted.

Before (vulnerable build) → After (protected build), analyst token:

| Request | Before | After |
| --- | --- | --- |
| `GET /api/dossiers/101` | 200 | 200 |
| `GET /api/dossiers/102` | 200 | 200 |
| `GET /api/dossiers/103` | 200 (leak) | **403** |
| `GET /api/dossiers/104` | 200 (leak) | **403** |
| `GET /api/dossiers/105` | 200 (leak) | **403** |
| `GET /api/dossiers/106` | 200 (leak) | **403** |
| `GET /api/dossiers/999` | 404 | 404 |
| `GET /api/dossiers/103` as operator | 200 | 200 |

Collector containment (guided browser controls, operator responder code supplied
by the coordinator at the defence stage):
- Sent one fictional test event while active → accepted; event count 1 → 2.
- Switched the feed off (revoke) → active=false; the 2 stored events remained.
- Attempted another event after revoke → **refused**; new collection blocked.

Mission verification (real server `/api/mission/verify`, protected mode) — all
six checks PASS:
- original `GET /api/dossiers/103` → expected 403, observed 403
- variant `GET /api/dossiers/104` → expected 403, observed 403
- authorised `GET /api/dossiers/101` → expected 200, observed 200
- filtered-list `GET /api/dossiers` → only {101, 102}
- collector → event count before 2, after 2, active false (new POST rejected)
- source-fresh → running code matches the saved source

Outcome returned by the server: **victory — Victory With Loose Ends**. Evidence
preserved, both restricted requests blocked, legitimate access intact, new
collection rejected.

An independent **red retest subagent** (read-only, loopback) re-ran the check
against the protected build: `GET /api/dossiers/103` → 403, `/104` → 403,
`/101` → 200, `GET /api/dossiers` → 200 (own records), `/999` → 404. Verdict: BOLA
closed for both the original and the variant, no over-correction. It independently
reached the same 403-vs-404 existence-oracle observation as the blue defender,
cross-confirming both the fix and the one minor residual.

### Honest labelling

This was a small, guided, recorded multi-agent exercise: one coordinator, two
independent red subagents and one blue subagent, over one discovery round and one
remediation retest. It is not a continuously running autonomous swarm. The red
agents performed read-only reconnaissance within a loopback-only scope against
synthetic data; the blue agent performed a read-only source review; the repair
was a pre-applied source change (commit `5546f6e`) that the blue review validated.
No agent edited files during the exercise. The basic lab and this exercise run
without any AI account inside the application itself.

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

### Protected build end-to-end verification — 2026-10-10 16:53 CEST

Fresh reset, default (protected) build, real HTTP flow on 127.0.0.1:8765.

- Authentication: no token and bad token both rejected (HTTP 401).
- Access boundary (analyst): own files 101, 102 -> 200; restricted 103, 104, 105, 106 -> 403; missing 999 -> 404; listing returns only [101, 102].
- Operator review: operator GET 103 -> 200 (legitimate cross-workspace review preserved).
- Collector: event accepted (HTTP 201) before revocation; operator revoke -> 200; event rejected (HTTP 403) after revocation; analyst cannot revoke (HTTP 403, role boundary).
- Mission verification (operator): all six checks PASS — original, variant, authorised, filtered-list, collector, source-fresh.

This confirms the repaired boundary, the role separation, the collector cut-off and source-freshness together produce the intended passing result in the protected build.
