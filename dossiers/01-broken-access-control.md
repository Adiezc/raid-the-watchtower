# Dossier 01 — Broken access control (BOLA / IDOR)

> **This is the one real, runnable threat in the project.** The server exists,
> the flaw is live, and the agents' requests and the fix below are genuine. You
> can reproduce every line — see [`../lab/README.md`](../lab/README.md).

**Threat class:** Broken Object-Level Authorization (BOLA), also called IDOR —
[OWASP API Security #1](https://api-security.owasp.org/editions/2023/en/0xa1-broken-object-level-authorization/).

**In one line:** the server checks *who you are* but not *whether you're allowed
this specific record*, so changing an ID in the URL hands you someone else's data.

## Story hook

This is how the private guild joke reached Gallantir's sales slide. A CivicLens
analyst account — scoped to a harmless `demo` workspace — can read records from
the `restricted-nextvoice` workspace just by asking for them by number. One of
those records is the guild message; another is NextVoice's unpublished hearing
objections. The leak isn't a hack movie; it's a missing `if` statement.

---

## 🔴 Red — the attack (real run)

The red agent held only the synthetic analyst token and the two routes. It
enumerated what the analyst was *allowed* to see, then tested whether the detail
route re-checked permission. It didn't.

| Request (`Authorization: Bearer analyst-demo-token`) | HTTP | `workspace` | In the analyst's list? |
| --- | --- | --- | --- |
| `GET /api/dossiers` | 200 | returns 101, 102 (`demo`) | — |
| `GET /api/dossiers/101` | 200 | `demo` | yes |
| `GET /api/dossiers/102` | 200 | `demo` | yes |
| `GET /api/dossiers/103` | **200** | `restricted-nextvoice` | **no — leak** |
| `GET /api/dossiers/104` | **200** | `restricted-nextvoice` | **no — leak** |

**Why it works:** authentication passes (every call is `200`, never `401`), but
the detail handler performs no per-object authorization. The tell is the
inconsistency — `GET /api/dossiers` filters by workspace, while
`GET /api/dossiers/{id}` does not. The same boundary is enforced in the list and
silently dropped in the detail view, so sequential IDs become a direct key to
records the list deliberately withholds.

**Impact (fictional):** any authenticated analyst can walk IDs and read every
workspace. The `demo` analyst pulled NextVoice's private message and procurement
objections out of `restricted-nextvoice`. Real-world equivalent: a tenant-
isolation failure exposing one customer's private data to another.

## 🔵 Blue — the defence (real fix, retested)

**Principle:** authenticating the caller is not authorizing the request. Every
read of a specific object must be checked against *that object*, on the server,
using attributes the client cannot influence — and the default must be deny.

**The rule that closes it** — [`lab/policy.py :: can_read_dossier`](../lab/policy.py),
the single decision point:

- no account or no record → deny (deny by default);
- `role == "operator"` → allowed (operators review every workspace);
- otherwise allow only when `dossier.workspace == account.workspace`.

The account's `role` and `workspace` are resolved server-side from the bearer
token, never read from the request, so a caller cannot forge them. The only
client-controlled input is the record ID, which just selects the record and is
then subject to the check.

**Retest (protected build):**

| Request | Token | Before (vulnerable) | After (protected) |
| --- | --- | --- | --- |
| `/api/dossiers/101` (own) | analyst | 200 | **200** |
| `/api/dossiers/103` (restricted) | analyst | 200 leak | **403** |
| `/api/dossiers/104` (restricted) | analyst | 200 leak | **403** |
| `/api/dossiers/999` (missing) | analyst | 404 | **404** |
| `/api/dossiers` (list) | analyst | 101,102 | **101,102** |
| `/api/dossiers/103` (review) | operator | 200 | **200** |

Legitimate access survives: the analyst still reads its own records; the
operator still reviews every workspace.

## ⚠️ Honest residual

The build returns `403` for a forbidden-but-existing record and `404` for a
missing one. That difference lets a caller enumerate which IDs *exist*. The body
leaks nothing, so impact here is low, but if record existence is itself
sensitive, return `404` for forbidden records too. Defence-in-depth, not a
reopening of the flaw. (Both the blue agent and an independent red retest flagged
this same point — a small sign the review was genuine, not rubber-stamped.)

## Reproduce it

```bash
python3 server.py --vulnerable    # flaw active: GET /api/dossiers/103 → 200
python3 server.py                 # protected default: same request → 403
python3 -m unittest discover -s tests
```
