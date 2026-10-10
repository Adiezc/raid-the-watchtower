# Investigation notes

Participant session: Claude (Opus) played the guided investigation end to end on
2026-10-10 at Adrian's request ("go through it as if you were a user and check
everything"). This is a Claude-as-participant walkthrough, not Adrian's own
session. Run `run-9f4b3eb9ce20`, vulnerable build, local target `127.0.0.1:8765`.

The initial observation and hypothesis below were recorded in the browser
notebook **before** any exploit was run and before any AI agent conclusion was
seen (checkpoint saved 2026-10-10 ~21:46 CEST).

## What I noticed

Rowan's joke from the private raid-night channel ("unionising the dragons")
appears word-for-word in Gallantir's CivicLens sales slide, labelled reference
CL-103. The channel is private, so a verbatim quote should not be reachable from
outside the guild.

## What I think might explain it

Something forwards the guild's private messages into CivicLens, probably the raid
companion add-on acting as a data collector. The slide reference CL-103 likely
maps to an internal record (dossier 103) tied to that collection. I also
suspected the platform may hand restricted records to any signed-in account, so I
tested whether the analyst account could open record 103 even though it is not in
the permitted list (101, 102). This was recorded as a hypothesis before testing.

## What the real response showed

Recon first: `GET /api/dossiers` as the analyst returned only CL-101 and CL-102,
both in the `demo` workspace. The list endpoint filters correctly.

Access test, reproduced both by API and through the browser's numbered record
field:

- `GET /api/dossiers/101` (my own record) -> HTTP 200 — legitimate access.
- `GET /api/dossiers/103` (CL-103, workspace `restricted-nextvoice`, not mine)
  -> **HTTP 200**, returning the full restricted record. The browser flagged it:
  "The server returned a record outside your account's permissions."

The leaked record 103 contained the collection route itself: the raid companion
integration (`integration-raid-companion`) forwarded the guild message
`message-raid-joke` (`event-0001`) into CivicLens, which is what surfaced on
slide CL-103. The record's "Sales preparation" label states Gallantir leadership
sought advance access to NextVoice's unpublished procurement arguments (fictional
story evidence).

Saved evidence (run `run-9f4b3eb9ce20`):
- `clue` — Private joke and matching sales slide.
- `restricted-dossier` — Restricted dossier 103 response (status 200, vulnerable
  mode, actor analyst).

## What I can and cannot establish

Established from evidence: a signed-in analyst account can read a restricted
record it was never granted, and that record ties the private joke to the raid
companion collection route and slide CL-103. This is broken object-level
authorisation (BOLA / IDOR): authentication succeeds but no per-object
permission check runs on the detail endpoint, even though the list endpoint
filters correctly.

Cannot establish from this lab alone: anything about real companies, real
surveillance, or motives beyond the fictional record text. All records are
synthetic. The "Sales preparation" narrative is a scripted story premise, not an
allegation about a real organisation.

## What changed and how we checked it

Repair (already in source, `lab/policy.py`, commit `5546f6e`): the detail
endpoint now decides access from the account's server-side workspace and role,
not from authentication alone. Operators retain cross-workspace review; the
deliberate flaw stays reachable only with `--training-vulnerable`.

Retest: see VERIFICATION.md and AGENT-ROUND-LOG.md for the protected-mode
verification run. After restarting protected on the same database, `GET
/api/dossiers/103` and `/api/dossiers/104` return HTTP 403 with no body, the
analyst's own `GET /api/dossiers/101` still returns 200, the list stays filtered
to {101,102}, the revoked collector rejects new events while the stored event
count is unchanged, and running code matches the saved source — the victory
outcome.

## Help I received

No hint levels were taken during this walkthrough (the solution was derived from
the evidence). The optional hint ladder in HINTS.md was left unused and the
`assistance` log is empty for this run. The guided browser controls and the
operator responder code were used as designed at the defence stage.
