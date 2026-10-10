# Raid the Watchtower

A fictional cybersecurity lab about defending a youth rights community from intrusive surveillance.

**Status: The beginner browser lab is ready. Ten automated checks and the builder browser walkthrough pass. Adrian's investigation, real source repair and final release remain to be completed.**

## The premise

NextVoice is a broader youth rights organisation. Some members meet in an MMO guild to have fun and stay connected globally. Their guild chats and community Discord have encountered increased surveillance.

Gallantir, a fictional intelligence contractor, markets its CivicLens platform as a noble protector of communities. NextVoice's campaign against purchases of systems that profile young people's political activity has caused potential customers to pause negotiations. Gallantir's leadership knowingly uses surveillance to protect sales. A raid companion add-on quietly forwards synthetic guild conversations into CivicLens.

The opening clue is a private guild joke quoted as a risk indicator in a Gallantir sales presentation. NextVoice presents its procurement objections tomorrow, while Gallantir prepares a rebuttal using unpublished arguments. The mission has three possible endings. The successful ending stops collection and pauses one fictional sale, while Gallantir remains powerful.

Your mission is to uncover evidence of this collection, demonstrate a permission failure in the local platform and protect the community by cutting off the mock data feed and fixing the access boundary.

All organisations, people, messages, allegations and records are fictional. Discord is referenced as part of the story. The lab uses a Discord-style mock interface and never connects to Discord, an MMO or any external service. Gallantir is not affiliated with any real company.

## Start here

- No technical experience is required for the guided session. Codex handles setup and the source repair. You use the browser, read clues and describe what you notice.
- On this Mac, [Start Training Lab.command](Start%20Training%20Lab.command) launches the explicit educational version and opens your default browser. Keep its window open while playing. If Codex has already started the lab, use the supplied browser link instead.
- The current baseline deliberately contains one permission flaw. Protected startup will be added by the real blue-agent repair during the session. This is not yet a completed release.

![The beginner starting screen](docs/screenshots/guild-start.jpg)

- [Build plan for 10 October, with a 20:00 Brussels deadline](docs/BUILD-PLAN.md)
- [One-day plan](docs/ONE-DAY-PLAN.md)
- [Player briefing](docs/PLAYER-BRIEF.md)
- [Completion checklist](docs/COMPLETION-CHECKLIST.md)
- [Story specification and ending conditions (spoilers)](docs/STORY.md)
- [Continuation notes](docs/HANDOFF.md)
- [Optional progressive hints](docs/HINTS.md)
- [Sources and limits](docs/SOURCES.md)

## Setup for technical reviewers

Python 3.9-compatible source uses the standard library, SQLite and local browser assets. The tested local runtime is Python 3.9.6. There are no application API keys, dependencies to install or external services.

```sh
python3 server.py --training-vulnerable --open-browser
python3 -m unittest discover -s tests -v
```

The server binds to `127.0.0.1:8765`. Stop it before resetting the fixture:

```sh
python3 server.py --reset
```

Reset starts a new mission and restores invented records and an active mock feed. It preserves previous exported evidence. An ordinary restart keeps the active mission and revocation state. Runtime files live in the ignored `var/` folder; exports live in `evidence/<run-id>/`.

The supplied analyst token is `analyst-demo-token`. Operator and collector credentials are separate, synthetic training passes. Codex supplies the responder code at the defence stage. The browser handles ordinary request syntax for the participant; technical reviewers can inspect the backend or run these commands.

## Verification and attribution

Ten baseline checks passed on 10 October 2026. They cover the real permission failure, authentication, role boundaries, collector acceptance and revocation, restart/reset behaviour, evidence exports, hint recording and verification freshness. The protected source repair, actual participant walkthrough and live red/blue exercise remain pending.

Codex agents implement the lab and its interface. Adrian directs and performs the guided investigation. The report will distinguish the work each actually completed. Builder QA is kept separate from participant evidence. See [the agent round log](docs/AGENT-ROUND-LOG.md).

The intended learning outcome is a reproducible example of reconnaissance, broken object-level authorisation, evidence handling, credential revocation and defensive retesting. The project does not claim practical phishing, malware-analysis or DDoS-testing experience.

The planned AI component uses a small Codex agent team: A red scout, an independent red validator and a blue defender, coordinated with the participant. One discovery round is followed by remediation and retesting. Actual exercise agent work will be recorded with evidence; no red/blue exercise agents have run yet. The local application will not require an AI account or embedded API credentials.

## Intended presentation

The interface is a compact desktop client. A Discord-style archived guild channel uses an engraved watchtower crest and small fantasy portraits. CivicLens is a cold corporate record browser with table-like record rows and an actual request console. The defence view uses a black and green terminal, displaying the real session and verification results. A case-file inspector keeps evidence and notes alongside the current view. There is no simulated terminal activity.

Design references are [Discord's channel layout](https://support.discord.com/hc/en-us/articles/360045138571-Beginner-s-Guide-to-Discord) and [terminal panes](https://learn.microsoft.com/en-us/windows/terminal/). The glyphs and portraits are local SVG drawings; no external art or remote fonts are loaded.

## Publication

The planned final repository will contain a local lab, synthetic fixtures, investigation evidence, verified fixes and an honest account of the participant's work. The agreed target is to finish the local exercise, publish an approved v1.0 GitHub release and archive the repository by 20:00 Brussels time on 10 October 2026. Public release and archival have not happened. The intended repository name is `raid-the-watchtower`.
