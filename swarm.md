# The agent swarm

This project's centre of gravity is not the lab. It is the **AI agent swarm**
that works the case, and the human who directs it. The lab exists to give the
swarm one real thing to attack and defend. Everything else is the swarm applying
the same red/blue method to a wider set of threats.

## Why this shape

Security is moving toward AI-assisted offence and defence. The interesting
question is no longer "can a model write a payload." It is **can a small team of
specialised agents, directed by a human, reason about an attack from both sides
and reach a defensible conclusion?** This project is a hands-on answer at a small
scale, built and narrated so a non-specialist can follow it.

The human role here is deliberate. **I direct the rounds, set scope and decide
what to trust.** The agents are fast and broad. They also confidently state wrong
things. Someone has to point them, keep them in bounds and verify the output.
That division of labour, orchestration and judgement on top of breadth and speed
underneath, is the whole thesis.

## The roles

| Agent | Job | Given | Not given |
| --- | --- | --- | --- |
| **Red scout / operator** | Probe the target, find a weakness, show how the attack lands | The brief and a synthetic account | The fix, the source, the answer |
| **Red validator** | Independently reproduce the finding with exact evidence | The same scope | The scout's conclusions |
| **Blue defender** | Review the code and design, define the fix, prove it closes the hole without breaking legitimate use | Source and logs | Permission to break scope |
| **Human coordinator (me)** | Set scope and order, review each result, decide what is real, verify the outcome | Everything | (nothing withheld) |

Two independent red agents matter. A *proposed* exploit is not a *confirmed*
finding until someone reproduces it without seeing the first agent's answer.

## How a round runs

1. **I record a hypothesis first**, before the agents report, so their answers
   inform rather than replace the human read.
2. **Red discovery and validation.** The scout finds, the validator independently
   reproduces, both log exact request/response evidence.
3. **Blue remediation.** The defender proposes the fix (for the real lab, a source
   change) and explains what legitimate behaviour must keep working.
4. **Red retest.** The same request and one related variant are retried against
   the fixed build.
5. **I verify** the outcome against actual results and write it up honestly,
   including disagreements and anything the agents got wrong.

## Run the swarm yourself

The round above is not just described, it is a runnable script. [`swarm/`](swarm/)
holds the orchestrator ([`run_exercise.py`](swarm/run_exercise.py)), the role
prompts ([`roles.py`](swarm/roles.py)) and captured [`transcripts/`](swarm/transcripts/).
The orchestrator starts the lab, gives each agent one scope-locked read-only HTTP
tool, runs the loop and writes the transcripts.

```bash
python3 swarm/run_exercise.py --self-check   # no API key: proves the plumbing and the scope guard
python3 swarm/run_exercise.py                # full run (needs the anthropic SDK and a key)
```

The scope is enforced in two places at once: the role prompt tells each agent the
boundary, and the `http_get` tool enforces it in code (only GET, only the lab's
own `/api/` routes). A model can be talked into things; the tool cannot. See
[`swarm/README.md`](swarm/README.md).

## What is real versus illustrative

Being honest about this is the point, not a disclaimer.

- **Real.** The broken-access-control lab in
  [`dossiers/01`](dossiers/01-broken-access-control.md) is a running server. The
  agents' requests, status codes and the fix are genuine. You can reproduce them
  (see [`lab/README.md`](lab/README.md)). The prompt-injection study in
  [`dossiers/06`](dossiers/06-prompt-injection.md) is also real: a poisoned
  record, two real agent runs and the code-enforced scope guard
  (`python3 swarm/run_exercise.py --injection-demo`).
- **Illustrative.** The other four threats
  ([phishing](dossiers/02-phishing.md),
  [trojans](dossiers/03-trojans.md),
  [worms](dossiers/04-worms.md),
  [DDoS](dossiers/05-ddos.md)) are **safe, synthetic analyses.** The swarm
  explains how the attack works and how blue detects and counters it, set in the
  fictional world. They contain **no working attack code, malware, phishing kits
  or load-generation tooling**, by design. That is both the ethical line and the
  honest-portfolio line: this showcases understanding and orchestration, not a
  weapons cache.

## Where this is going (and its limits)

AI red- and blue-teaming is an active research and product direction. This lab
illustrates one small workflow. It does **not** show that autonomous swarms
replace security professionals or scale cleanly to production.

- Microsoft describes red-team agents for scoped assessment workflows (Project
  Perception, limited preview):
  <https://learn.microsoft.com/en-us/security/agentic-security/agentic-security-red-agent-considerations>
- ARTEMIS, a multi-agent penetration-testing framework (research paper):
  <https://arxiv.org/abs/2512.09882>
- CyberBattleSim studies red/blue reinforcement-learning agents in simulation, a
  different approach from LLM agents, not validation of this design:
  <https://arxiv.org/abs/2304.11052>
- PentAGI (`vxcontrol/pentagi`, MIT) is the production-scale instance of this
  project's thesis: a human-authorized multi-agent system (Orchestrator,
  Researcher, Developer, Executor, plus supervision agents like Reflector and
  Adviser) that runs real security tools inside Docker sandboxes, with per-agent
  hard tool-call limits, a pgvector knowledge store and full observability. This
  project is a deliberately tiny, loopback-only, human-in-the-loop demonstration
  of the same red/blue orchestration idea. Several design choices here (the
  task decomposition, the per-agent call caps, the scope guard) echo patterns
  PentAGI implements at scale: <https://github.com/vxcontrol/pentagi>
- HexStrike AI (`0x4m4/hexstrike-ai`, MIT) is a third point on the autonomy
  spectrum: an MCP server exposing 150+ security tools to any MCP client, with
  an intelligent decision engine for tool selection and failure recovery. It is
  a useful contrast rather than a template here, because its scope control is
  guidance-level (run in isolated VMs, keep oversight) rather than enforced in
  code. This project takes the opposite stance on purpose: one read-only tool,
  scope enforced in code, and a human who verifies before anything is trusted.
  <https://github.com/0x4m4/hexstrike-ai>

The honest limit: agents are powerful force-multipliers and poor sole deciders.
The human who can tell *correct* from *actually right* is still the job.
