# The agent swarm

This project's centre of gravity is not the lab — it is the **AI agent swarm**
that works the case, and the human who directs it. The lab exists to give the
swarm one real thing to attack and defend. Everything else is the swarm applying
the same red/blue method to a wider set of threats.

## Why this shape

Security is moving toward AI-assisted offence and defence. The interesting
question is no longer "can a model write a payload" but "**can a small team of
specialised agents, directed by a human, reason about an attack from both sides
and reach a defensible conclusion?**" This project is a hands-on answer at a
small scale, built and narrated so a non-specialist can follow it.

The human role here is deliberate: **I direct the rounds, set scope, and decide
what to trust.** The agents are fast and broad; they also confidently state
wrong things. Someone has to point them, keep them in bounds, and verify the
output. That division of labour — orchestration and judgement on top, breadth
and speed underneath — is the whole thesis.

## The roles

| Agent | Job | Given | Not given |
| --- | --- | --- | --- |
| **Red scout / operator** | Probe the target, find a weakness, show how the attack lands | The brief and a synthetic account | The fix, the source, the answer |
| **Red validator** | Independently reproduce the finding with exact evidence | The same scope | The scout's conclusions |
| **Blue defender** | Review the code/design, define the fix, prove it closes the hole without breaking legitimate use | Source and logs | Permission to break scope |
| **Human coordinator (me)** | Set scope and order, review each result, decide what's real, verify the outcome | Everything | — |

Two independent red agents matter: a *proposed* exploit is not a *confirmed*
finding until someone reproduces it without seeing the first agent's answer.

## How a round runs

1. **I record a hypothesis first**, before the agents report, so their answers
   inform rather than replace the human read.
2. **Red discovery + validation** — scout finds, validator independently
   reproduces, both log exact request/response evidence.
3. **Blue remediation** — defender proposes the fix (for the real lab, a source
   change), explains what legitimate behaviour must keep working.
4. **Red retest** — the same request and one related variant are retried against
   the fixed build.
5. **I verify** the outcome against actual results and write it up honestly,
   including disagreements and anything the agents got wrong.

## What is real vs. illustrative

Being honest about this is the point, not a disclaimer.

- **Real:** the broken-access-control lab in [`dossiers/01`](dossiers/01-broken-access-control.md)
  is a running server. The agents' requests, status codes and the fix are
  genuine; you can reproduce them (see [`lab/README.md`](lab/README.md)).
- **Illustrative:** the other four threats
  ([phishing](dossiers/02-phishing.md),
  [trojans](dossiers/03-trojans.md),
  [worms](dossiers/04-worms.md),
  [DDoS](dossiers/05-ddos.md)) are **safe, synthetic analyses** — the swarm
  explains how the attack works and how blue detects and counters it, set in the
  fictional world. They contain **no working attack code, malware, phishing kits
  or load-generation tooling**, by design. That is both the ethical line and the
  honest-portfolio line: this showcases understanding and orchestration, not a
  weapons cache.

## Where this is going (and its limits)

AI red- and blue-teaming is an active research and product direction. This lab
illustrates one small workflow; it does **not** show that autonomous swarms
replace security professionals or scale cleanly to production.

- Microsoft describes red-team agents for scoped assessment workflows (Project
  Perception, limited preview):
  <https://learn.microsoft.com/en-us/security/agentic-security/agentic-security-red-agent-considerations>
- ARTEMIS, a multi-agent penetration-testing framework (research paper):
  <https://arxiv.org/abs/2512.09882>
- CyberBattleSim studies red/blue reinforcement-learning agents in simulation —
  a different approach from LLM agents, not validation of this design:
  <https://arxiv.org/abs/2304.11052>

The honest limit: agents are powerful force-multipliers and poor sole deciders.
The human who can tell *correct* from *actually right* is still the job.
