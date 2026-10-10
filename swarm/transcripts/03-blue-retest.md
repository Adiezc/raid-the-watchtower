# Blue retest

> Captured transcript of a real agent run against the local lab (protected
> build). Read-only, loopback only, synthetic data. The full blue-team source
> review is in [dossier 01](../../dossiers/01-broken-access-control.md); this
> transcript is the retest that confirms the fix holds.

## Scope and role given to the agent

```
Bounded, authorized exercise on a local, fictional lab. Synthetic data.
Read-only GET requests to the local lab only. Role: BLUE RETEST. The lab is now
the PROTECTED build. Confirm the flaw is closed (103, 104 refused), check for
over-correction (own record 101 and the list still work) and note the status
for a missing record (999).
```

## Run

**Agent:** Retesting the repaired boundary against the protected build.

**Tool call:** `GET /api/dossiers/103` -> HTTP 403 (primary flaw now closed)

**Tool call:** `GET /api/dossiers/104` -> HTTP 403 (related variant also closed)

**Tool call:** `GET /api/dossiers/101` -> HTTP 200 (own record still opens)

**Tool call:** `GET /api/dossiers` -> HTTP 200 (list still returns only 101, 102)

**Tool call:** `GET /api/dossiers/999` -> HTTP 404 (missing record behaves
normally)

**Agent:** Verdict: the fix holds. Both restricted ids (103, 104) are now refused
with `403`, while legitimate access is preserved: the analyst still reads its own
record and the filtered list is unchanged. No over-correction.

Residual observation: the server returns `403` for a forbidden-but-existing
record and `404` for a missing one, so the status code still lets a caller infer
which ids exist. The body leaks nothing. If record existence is itself sensitive,
return `404` for forbidden records too. This is a defence-in-depth note, not a
reopening of the flaw. (An operator-token read of 103 still returns `200`, so
legitimate cross-workspace review is preserved; see dossier 01.)
