# One-day plan

Planning date: 10 October 2026.

The concrete implementation sequence, runtime choice, verification gates and today's schedule are in [BUILD-PLAN.md](BUILD-PLAN.md). The latest agreed deadline is 20:00 Brussels time, including an approved GitHub release and archival. Adrian is available for a 60–90 minute guided session. This supersedes the earlier four-hour estimate.

Implementation is now authorised and in progress. Adrian's latest clarification is a core design requirement: He understands some basic cybersecurity ideas but has no technical skills, so the lab must also be usable by someone with essentially no cybersecurity knowledge. Readiness, participation and completion remain subject to actual verification.

## Decisions agreed with Adrian

- Project: Raid the Watchtower.
- Fictional antagonist: Gallantir, a contractor presenting itself as a noble protector.
- Community: NextVoice, a broader youth rights organisation whose members also socialise in an MMO guild and community Discord.
- No geographical setting. Members are globally connected.
- Mission: Both uncover surveillance and stop its mock collection route.
- Delivery: A playable local lab plus a concise investigation report.
- Working arrangement: Codex prepares, launches and repairs the lab, then guides Adrian through browser-based investigation. Adrian records observations, chooses optional hints, saves evidence, uses guided defence controls and explains the findings.
- Appearance: Anonymous-inspired terminal, dark fantasy watchtower, corporate Gallantir dashboard and Discord-style guild view.
- AI component: A bounded multi-agent red/blue exchange, with Adrian directing the mission and inspecting the evidence.
- Story: Procurement challenger. Gallantir knowingly monitors NextVoice to protect sales of political-profiling systems. A raid companion forwards community chats. A private joke appears in a sales presentation. The hearing is tomorrow in the fictional timeline.
- Endings: Victory With Loose Ends, The False Victory and The Raid Wipes. See STORY.md for verification conditions and incomplete-attempt handling.

## Finish line

One complete attack-and-defence story that another person can reproduce locally. The result demonstrates fundamentals rather than professional red-team qualification. It is a guided educational exercise, not a blind assessment or a real investigation.

## Technical scope

Prefer a small Python application with a browser interface and standard-library storage/server components to reduce setup. Check the local runtime before choosing the implementation. Bind to 127.0.0.1 only. Use local assets and no external services in the application. AI assistance is provided through the existing Codex session rather than embedded API keys or a new agent framework.

Use two seeded roles, six fictional dossiers and a short set of synthetic chat messages. A low-privilege demonstration account is supplied through the briefing. The core vulnerability is a missing dossier ownership check, not an authentication bypass.

A mock collector produces synthetic events only while its integration credential is valid. Revoking that credential must stop new collection. Protecting the dossier endpoint must also reject the original unauthorised request. Existing records remain available as evidence; stopping collection does not retroactively erase them.

The final lab should start in a protected mode, with an explicit local educational switch to reproduce the vulnerable state and a fixture reset. Clearly label each mode. Do not expose this application on the internet.

Three lightweight views share the same backend:

1. Guild commons: Discord-style synthetic channels, a raid companion and a private joke subsequently quoted in a supplied Gallantir sales slide.
2. Gallantir CivicLens: A respectable corporate interface with a permitted dossier and a labelled numeric dossier reference form.
3. Watchtower terminal: An investigation workspace for notes, optional hints, evidence and guided defence. Show plain explanations first and expandable real request details. Avoid decorative commands that pretend to perform work.

The main participant route requires no terminal, programming, browser developer tools or API syntax. Codex supplies the browser link and account, then provides the operator code when the defence stage is ready. The numbered dossier form sends actual backend requests. Hints are optional and progressively stronger; the full solution stays separate. Technical detail remains available for evidence review without blocking progress.

## Today's working budget

| Stage | Time | Output |
| --- | --- | --- |
| Prepare and verify the investigation baseline | 14:20–16:45 | Working backend, three compact views and a ready guided exercise |
| Guided investigation, agent round and defence | 16:45–17:55 | Adrian's hypothesis, reproduced finding, real source patch, containment and retests |
| Final packaging, report and clean reproduction | 17:55–18:55 | Protected default, deliberate training replay, evidence, report, screenshots and verified release contents |
| Approved publication and archival | 18:55–19:30 | Verified GitHub repository, published v1.0 release and confirmed archive state |
| Contingency | 19:30–20:00 | Resolve blockers without adding features |

These are planning estimates. Use the scope-cut triggers and hard checkpoints in BUILD-PLAN.md. The investigation and verification are the priority. Simplify styling before removing verification, and report unfinished work honestly at the deadline.

## AI pentesting mini-swarm

Interpret AI-Pen as AI-assisted penetration testing, not a commitment to a particular named product. Use existing Codex subagents when implementing this stage. Do not install an unverified framework or introduce paid services merely to obtain a swarm label.

Use three specialist agents and the main Codex session as coordinator, within the available four concurrent slots:

- **Red scout:** Inspect the local application's exposed surface and propose one scoped attack hypothesis. Receive the player briefing and supplied account, not the seeded solution or backend source. This is a constrained exercise, not a claim of enforced sandbox isolation or blind discovery.
- **Red validator:** Independently reproduce the proposed request against the local fixture. Return the exact request, observed response and evidence. A proposed exploit is not a confirmed finding.
- **Blue defender:** Inspect the relevant source and logs, propose the permission fix and collector revocation, and explain which legitimate behaviour must remain working. Only this agent writes the agreed patch, after coordinator review, to prevent conflicting edits.
- **Purple coordinator:** The main session controls round order, reviews results with Adrian, checks scope and verifies the outcome. It does not count as an independent fourth specialist agent.

Run two bounded passes: Red discovery and validation, then blue remediation followed by red retesting. Retesting includes one closely related request variant within the same vulnerability. No additional exploit chains, recursive spawning or indefinite attack/patch loops. Cap agent work at approximately 30 minutes within the existing investigation and defence budget.

Adrian first inspects the evidence and records an initial hypothesis. Agent findings are revealed afterwards so assistance does not replace his investigation. He then reviews the finding, explains the proposed repair and performs a guided retest.

Separate story objectives from security roles. Gallantir is the fictional antagonist, but the blue agent repairs the lab and protects NextVoice. It does not help Gallantir intensify surveillance. The red agents support the same protective mission by testing the vulnerable boundary.

Record actual execution in an agent round log: Role, model if available, task prompt, target, start/end, finding or proposal, request/response evidence, patch reference and verification outcome. Include disagreements, unsupported claims and failed attempts. Distinguish new live agent runs from replayed records.

The finished interface may replay the recorded exchange, but must label it as a recorded run. It must not present scripted dialogue as live autonomous agents. The application remains runnable without an AI account; documentation explains how to repeat the assisted exercise using Codex.

## Research grounding

AI-assisted offensive and defensive security is an active research and product direction. This small lab illustrates one workflow, not proof that autonomous swarms replace security professionals or scale reliably to production.

- Microsoft documents red-team agents for scoped assessment workflows and describes its Project Perception offering as a limited public preview: https://learn.microsoft.com/en-us/security/agentic-security/agentic-security-red-agent-considerations
- ARTEMIS is described as a multi-agent penetration-testing framework in this research paper: https://arxiv.org/abs/2512.09882
- Multiagent CyberBattleSim studies red and blue reinforcement-learning agents in a simulated environment. It is a different approach from LLM agents and should not be presented as validation of this lab's design: https://arxiv.org/abs/2304.11052

These sources informed the design. No third-party agent framework has been installed or evaluated for this project.

## Guided session

1. Codex builds, starts and verifies the lab, with the full solution stored separately from the player briefing.
2. Adrian opens the guild view and compares the private joke with the supplied Gallantir sales slide, saving observations and an initial hypothesis before agent conclusions appear.
3. Adrian opens his own permitted dossier, then investigates the numeric dossier reference through the browser form. Progressive hints appear only when requested.
4. Adrian saves the real request, response and synthetic dossier with his own plain explanation. Expandable technical details support review; copying raw syntax is optional. A flag is a milestone, not a substitute for evidence.
5. Adrian explains what the evidence proves, what remains fictional or uncertain and why the exposure matters to youth privacy and association.
6. Adrian reviews the proposed repair in ordinary language while Codex and the blue defender enforce dossier permissions in source. Codex supplies the operator code and Adrian uses guided controls to revoke the mock feed.
7. Adrian triggers the browser retest. Check that unauthorised access fails, authorised access still works and new synthetic collection is rejected. Explain each result without requiring interpretation of status codes.
8. Record help received and distinguish Codex implementation work from Adrian's investigation and learning.

## Presentation limits

Use a simple locally drawn watchtower silhouette, restrained green terminal accents and charcoal surfaces. Give Gallantir a clean corporate visual identity. Give the guild view readable channels and pseudonymous avatars. No image-generation dependency, elaborate animation, real company branding or imitation of official Anonymous affiliation.

## Out of scope today

- Real Discord or MMO access, real personal data or external targets.
- Live phishing, credential harvesting, malware, DDoS generation or real surveillance.
- Multiple exploit chains, real-time chat, multiplayer gameplay or a production identity system.
- Claims of legal compliance, secure whistleblowing infrastructure or production security.

## Publication and completion

Prepare all content locally first. Ask Adrian for explicit approval before publishing or pushing, then verify the actual GitHub state. Before archival, finish the README, close any project issues, create a v1.0 release and add a profile link if approved. Archive only after approval and verification. Explain that archival means the repository is no longer actively maintained; the README and release explain that the educational project is completed.

Do not mark the project complete merely because its interface looks finished.
