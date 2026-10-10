# Raid the Watchtower — exercise report

**Date:** 2026-10-10 (evening, CEST)
**Run:** `run-9f4b3eb9ce20`, local target `http://127.0.0.1:8765` (loopback only)
**Who did this:** Claude (Opus), playing the guided investigation and coordinating
a bounded red/blue agent round, at Adrian's request. This stands in for, but does
not replace, Adrian's own participation. All organisations, people, messages and
records are fictional and synthetic.

## 1. What this exercise was

A self-contained training lab demonstrating one real backend access-control flaw —
**broken object-level authorisation (BOLA / IDOR, OWASP API Security Top 10 #1)** —
inside a fictional story: a youth-rights guild (NextVoice Nightwatch) discovers its
private chat quoted in a surveillance vendor's (Gallantir / CivicLens) sales slide,
and the player must prove the leak, preserve evidence, cut the feed and verify the
fix. Three endings are possible; the success ending is *Victory With Loose Ends*.

## 2. The finding (fact, from evidence)

The CivicLens API authenticated a caller but did not check whether that caller was
allowed to read the specific record requested:

- `GET /api/dossiers` (list) correctly returned only the analyst's own records
  (CL-101, CL-102, workspace `demo`).
- `GET /api/dossiers/103` and `/104` (`restricted-nextvoice`), `/105`
  (`restricted-supplier`) and `/106` (`restricted-operations`) all returned **HTTP
  200** to the same analyst token — records in workspaces the analyst was never
  granted.

The leaked record 103 itself contained the story's collection route: the
`integration-raid-companion` integration forwarded the private guild message
(`event-0001`) into CivicLens, which is what surfaced on slide CL-103. So the
single flaw both (a) is a genuine authorisation defect and (b) explains the
narrative leak.

The tell is the **inconsistency**: the list endpoint knew the analyst's scope and
filtered on it; the detail endpoint did not apply the same check.

## 3. What two independent AI red agents found

Two red subagents probed the vulnerable build independently (neither saw the
other's work), read-only, loopback-only:

- Both named the vulnerability class as BOLA/IDOR on the detail endpoint.
- Both confirmed ids 103–106 leak across three distinct restricted workspaces —
  i.e. a systematic missing check, not one misconfigured record.
- A missing id (100 / 999) returned 404, showing the endpoint distinguishes
  "does not exist" from "exists but forbidden" — so the flaw was an absent
  ownership check, not a routing accident.

The convergence of two independent agents plus the coordinator's own manual probe
cross-validates the finding.

## 4. The repair and the blue review (fact)

Repair (commit `5546f6e`, `lab/policy.py`): the detail endpoint now decides access
from the caller's **server-side** workspace and role — allow only if the caller is
an operator or the record's workspace matches the caller's own. Authentication
alone is insufficient.

A blue subagent reviewed the repair (read-only) and judged it **sound and
complete**: it closes all of 103–106, preserves the analyst's own records and the
operator's legitimate cross-workspace review, and relies only on server-held
attributes — the browser can supply only the numeric id, not a forged workspace or
role. One honest residual was recorded: a forbidden-but-existing record returns 403
while a missing one returns 404, so the status code is a minor **existence oracle**
(no record content leaks). Suggested hardening: return 404 for forbidden records
too. Impact is negligible in this fixed lab; it is noted rather than fixed.

## 5. Retest and outcome (fact)

The lab was restarted into the protected default build on the same database
(evidence persisted). Against the repaired build, analyst token:

- Restricted 103–106 → **403**; own records 101/102 → **200**; missing 999 → 404;
  operator review of 103 → 200.
- Collector: one fictional event accepted while active (count 1→2), feed revoked
  (both events preserved), a post-revoke event **refused**.
- Real server verification (`/api/mission/verify`, protected mode): all six checks
  pass. Server outcome: **victory — Victory With Loose Ends**.

## 6. Facts vs. inference vs. fiction

- **Fact (evidence-backed):** the access-control flaw, the four leaked ids, the
  repair's effect, the collector revocation and the passing verification. These are
  real HTTP results against the local server, recorded with request/response logs
  and exported evidence files.
- **Inference:** that the list-vs-detail inconsistency indicates an absent
  object-level check (supported by source review) rather than data corruption.
- **Fiction:** NextVoice, Gallantir, CivicLens, the guild, the surveillance
  narrative, the "paused sale" epilogue and every record's contents. Nothing here
  is an allegation about any real organisation, and the lab connects to no external
  service.

## 7. Assistance and authorship (honest account)

- The lab and its interface were built by Codex/Claude agents in prior sessions.
- This investigation and the red/blue round were performed by Claude at Adrian's
  explicit request; it is labelled throughout as a Claude-run exercise, not
  Adrian's own session and not a live autonomous swarm.
- No optional hints were used; the solution was derived from the evidence.
- The red/blue "swarm" was one coordinator plus three bounded subagents over one
  discovery round and one remediation retest — a small guided exercise, recorded,
  not continuous autonomous activity.

## 8. Limitations

Loopback-only, synthetic data, one flaw class. The exercise demonstrates
reconnaissance, BOLA/IDOR, evidence handling, credential revocation and defensive
retesting. It does not demonstrate write/delete exposure (only GETs were tested),
unauthenticated bypass, phishing, malware analysis or DDoS testing, and makes no
claim about production systems or real companies.
