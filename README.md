# Raid the Watchtower

**An AI agent swarm, directed by a human, red-teams and blue-teams a set of
security threats — wrapped in a short fictional story.**

This is a portfolio project. It showcases two things: an understanding of how
common attacks work and how you defend against them, and the use of an **AI
red/blue agent swarm** to do that analysis — with a person in the loop to direct
the rounds and decide what to trust. One threat is a real, runnable lab; the rest
are safe, synthetic studies. Everything here is fictional and defensive.

> New to the project? Read [`story.md`](story.md) for the world, then
> [`swarm.md`](swarm.md) for how the agent team works. Then pick a dossier.

## The idea in one minute

Security is moving toward AI-assisted offence and defence. The real skill is no
longer only "write a payload" — it is **directing a team of specialised agents,
keeping them in scope, and verifying what they produce.** This project is a small,
honest demonstration of exactly that: a red scout and validator find and confirm,
a blue defender fixes and proves it, and a human coordinator sets scope and calls
what's real. See [`swarm.md`](swarm.md).

## The threats (dossiers)

Each dossier is a red/blue study: how the attack works 🔴 and how you detect and
stop it 🔵, set in the story, with an honest note on limits.

| # | Threat | Real or illustrative | Dossier |
| --- | --- | --- | --- |
| 01 | **Broken access control** (BOLA / IDOR) | **Real, runnable** — live server, real agent run, real fix | [01](dossiers/01-broken-access-control.md) |
| 02 | **Phishing** (credential theft) | Illustrative (safe, synthetic) | [02](dossiers/02-phishing.md) |
| 03 | **Trojans** (malware disguised as a tool) | Illustrative (safe, synthetic) | [03](dossiers/03-trojans.md) |
| 04 | **Worms** (self-spreading malware) | Illustrative (safe, synthetic) | [04](dossiers/04-worms.md) |
| 05 | **DDoS** (flooding a service offline) | Illustrative (safe, synthetic) | [05](dossiers/05-ddos.md) |

**Real vs illustrative is deliberate and stated up front.** Dossier 01 is a
running lab you can reproduce. Dossiers 02–05 are conceptual analyses — they
explain mechanics and defences and contain **no working attack code, malware,
phishing kits or load-generation tooling**, by design. That is both the ethical
line and the honest-portfolio line: this shows understanding and orchestration,
not a weapons cache.

## The one real demo

A tiny standard-library server with a genuine broken-object-level-authorization
flaw. No dependencies, loopback only, synthetic data.

```bash
python3 server.py --vulnerable    # flaw active:    GET /api/dossiers/103 → 200 (leak)
python3 server.py                 # protected default: same request → 403
python3 -m unittest discover -s tests
```

Full walkthrough in [`lab/README.md`](lab/README.md) and
[dossier 01](dossiers/01-broken-access-control.md).

## Honest account

- **Who built this:** the lab and the dossiers were produced with AI agents that
  I directed, scoped and reviewed. I am not claiming hands-on exploit-development
  experience; I am showing threat literacy and the ability to orchestrate and
  verify an AI red/blue team. That framing is the point, and it is true.
- **What's proven:** only dossier 01 is a live, reproducible result. The rest are
  analyses, labelled as such.
- **Scope:** fictional world, synthetic data, loopback only, defensive framing. No
  real people, companies, or systems are targeted; "Gallantir" is not a real
  company.

## References

- OWASP API1: Broken Object Level Authorization —
  <https://api-security.owasp.org/editions/2023/en/0xa1-broken-object-level-authorization/>
- UN Convention on the Rights of the Child, Articles 15–16 (association, privacy),
  context for the youth-rights framing —
  <https://www.unicef.org/child-rights-convention/convention-text>
- Python standard-library HTTP server (explicitly not for production) —
  <https://docs.python.org/3/library/http.server.html>
- AI red/blue research and tooling: see the "Where this is going" section of
  [`swarm.md`](swarm.md).

## Layout

```
README.md     story.md     swarm.md        LICENSE
server.py                  ← the one real, runnable flaw
lab/          policy.py, fixtures.json, README.md
tests/        test_lab.py  ← 7 checks
dossiers/     01…05        ← the red/blue threat studies
```

MIT licensed. Fictional throughout.
