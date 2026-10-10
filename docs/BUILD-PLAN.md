# Raid the Watchtower: Build plan

Date: 10 October 2026. All scheduled times are Brussels time.

**Target: A verified local lab, Adrian's guided investigation, an evidence-backed report and an approved GitHub v1.0 release, published and archived by 20:00.**

Status: Implementation authorised and in progress. Investigation readiness, Adrian's participation, the red/blue exercise and publication still require actual evidence. The story and learning scope remain those agreed in [ONE-DAY-PLAN.md](ONE-DAY-PLAN.md) and [STORY.md](STORY.md). This document governs today's implementation order and timing.

## What we will finish

One small browser application will contain the guild commons, Gallantir's CivicLens dashboard and the Watchtower investigation terminal. It will demonstrate a real dossier permission failure, preserve synthetic evidence, stop a mock collector and verify the defensive repair. Adrian will investigate it with guidance and take part in a bounded red/blue agent round.

Adrian has basic familiarity with cybersecurity ideas and no technical skills. Design the whole player journey for someone with essentially no cybersecurity knowledge. Codex handles setup, launch, account preparation and source changes. The participant uses a browser, reads short explanations, enters observations and makes guided choices. Command-line use, browser developer tools, programming and API syntax are not prerequisites.

The final package will contain the runnable source, synthetic fixtures, meaningful checks, a player briefing, a separate solution, actual request/response evidence, the reviewed patch, an agent round log, four inspected screenshots and a concise Markdown report. GitHub will receive the reviewed package and a v1.0 release before archival.

Completion has two distinct checks: The local exercise must work and the published release and archive state must be verified. A prepared package does not establish publication. A polished interface does not establish a working exercise.

## Today's schedule

The working schedule starts at 14:20 and uses 5 hours 40 minutes, including a 30-minute buffer. The hard stop is 20:00. If implementation starts later, record the actual start and apply the scope cuts below rather than move the deadline silently.

| Time | Work | Owner | Required result |
| --- | --- | --- | --- |
| 14:20–14:35 | Scaffold and check delivery access | Codex | Local Git repository, file structure, runnable server skeleton and early GitHub access/name check |
| 14:35–15:25 | Build backend and fixtures | Codex | Authenticated dossiers, intentional vulnerable baseline, synthetic ingestion, revocation, reset and evidence capture working through actual requests |
| 15:25–16:20 | Build the three views | Codex | Readable clues, guided dossier form, plain-language evidence and operator controls returning real backend results |
| 16:20–16:45 | Verify investigation readiness | Codex | Baseline checks pass, reset works and the beginner browser journey works without revealing the solution |
| 16:45–17:55 | Guided investigation and agent round | Adrian with Codex | Initial hypothesis, independently reproduced finding, reviewed source repair, revoked collector and actual retest evidence |
| 17:55–18:35 | Final packaging and report | Codex with Adrian's observations | Protected default, explicit vulnerable replay, post-packaging checks, report, agent log, solution and four screenshots |
| 18:35–18:55 | Fresh reproduction and release review | Codex | Clean-copy launch and tests pass; exact publication contents and release notes are ready for review |
| 18:55–19:20 | Publish approved package and v1.0 | Codex after Adrian's approval | GitHub content, default branch and published release are checked against the local package |
| 19:20–19:30 | Archive approved repository | Codex after Adrian's approval | Final README and release visible, unfinished work resolved and actual archived state confirmed |
| 19:30–20:00 | Contingency | Together as needed | Repair blockers and verify final state; no new features |

Adrian's main session is 16:45–17:55. Reserve brief review availability around 18:55 for publication and 19:20 for archival. Present concrete contents at each review point. If approval or access is unavailable, finish the local package and record the outstanding external step; do not call the full target achieved.

## Implementation decisions

The current machine has Python 3.9.6, SQLite 3.54.0 and Git 2.54.0. Python's HTTP server, SQLite, secrets and unittest modules were successfully imported during planning. Use Python 3.9-compatible code, a custom standard-library HTTP handler, SQLite and plain HTML, CSS and JavaScript. No package installation or front-end build pipeline is needed for this design. These are local runtime checks, not evidence that the future app works.

Bind the server to `127.0.0.1`, with `8765` as the proposed port. Provide one launch command, one fixture-reset command and one test command for Codex and maintainers. Final command names become verified README instructions after implementation. During Adrian's session Codex runs these steps and supplies the browser link; the player briefing must not require him to operate a terminal.

### Backend and data

Seed two account roles: An analyst with access to a small demonstration workspace and an operator with maintenance permissions. Seed six dossiers, including at least one analyst-authorised record and two distinct restricted records. Validate the supplied synthetic account token before every protected request in both modes. The intentional flaw is the missing object permission check after authentication.

Use four small tables: Accounts, dossiers, the collector integration and collected events. Keep short guild messages and the sales-slide clue in synthetic fixtures. Link the guild message, integration, collected event and dossier through explicit identifiers so the surveillance route can be established from evidence.

The list endpoint shows only the analyst's permitted records in both modes. The vulnerable detail endpoint returns a requested restricted dossier without checking its workspace. The repaired detail endpoint checks the authenticated account's server-side workspace permissions, with the documented operator exception. Never trust a workspace or role supplied by the browser.

This reflects the object-permission distinction described in [OWASP's BOLA guidance](https://api-security.owasp.org/editions/2023/en/0xa1-broken-object-level-authorization/): A caller may use the endpoint but still lack permission for the requested record. The final checks must cover every implemented dossier route.

| Proposed route | Purpose | Contract |
| --- | --- | --- |
| `GET /api/dossiers` | List permitted dossiers | Authenticated and filtered in both modes |
| `GET /api/dossiers/{id}` | Read one dossier | Vulnerable baseline lacks the object check; protected state enforces it |
| `POST /api/collector/events` | Submit one synthetic message | Accept only the seeded integration credential while it is active |
| `GET /api/collector/status` | Inspect integration and event count | Operator only |
| `POST /api/collector/revoke` | Disable new collection | Operator only; preserve earlier events |

Use an explicit operator action to simulate one collection event. This is enough to prove acceptance before revocation and rejection afterwards. A background stream is unnecessary today. Keep account tokens separate from the collector credential. Revocation must change persistent backend state, rather than just hide a button or display a success label.

Use fixed static-file routes, parameterised database statements and text-safe rendering. Do not serve the database, raw fixtures, solution or evidence folders through the application. The terminal's guided form sends local lab requests through the same API. Raw request details are expandable; the terminal is not a shell or a proxy to arbitrary URLs.

### A real blue repair and a replayable final lab

Build and locally checkpoint the vulnerable baseline before the guided session. Its initial launch must require an explicit educational flag. At this stage, final protected startup remains an implementation task and the application is not release-ready.

After Adrian's investigation and red validation, the blue defender edits the active dossier authorisation code. The coordinator reviews the proposed diff before it is applied. Save the actual before/after revisions or source hashes and patch. Adding the permission check is the code repair; revoking the integration credential is a separate containment action.

After remediation, package the patched path as the protected default. Preserve the baseline behaviour in one isolated training policy selected only by an explicit `--training-vulnerable` flag. There must be no browser control that silently disables authorisation. Display the active mode on every view. Repeat the full verification matrix after packaging because retaining the training path changes the final source.

The reset command restores synthetic accounts, dossiers and an active collector for a new exercise. It never changes the process's selected mode. Reset is not a repair. Keep completed evidence bundles outside the resettable database and retain them across reset and restart. A clean first launch or explicit reset starts a new incomplete mission. An ordinary restart preserves the active run and collection state; recheck assertions before awarding a final outcome.

### Three compact views

| View | Required content | Presentation |
| --- | --- | --- |
| Guild commons | Synthetic channels, raid companion, harmless private joke and the supplied sales slide quoting it | Warm community colours, readable messages and pseudonymous avatars |
| CivicLens | Own permitted dossier, numeric dossier reference form and plain explanation of the returned result | Clean corporate layout that contrasts with the community view |
| Watchtower terminal | Observation notes, optional hints, evidence saving, guided operator controls and verification results; expandable real request details | Charcoal surfaces, restrained green accents and a locally drawn watchtower silhouette |

Use one page with three tabs and shared CSS. The sales slide can be a designed panel rather than a separate presentation file. Four screenshots are sufficient: Opening clue, permission failure, protected retest and the verified outcome. No generated imagery, animation framework or agent-chat product is needed.

### Beginner acceptance criteria

- A new participant can read the private joke beside the sales slide and save an observation before receiving a proposed explanation.
- The supplied analyst account is ready to use. Opening its own permitted dossier establishes how the interface normally behaves.
- The investigation uses a labelled numeric dossier reference field and a button that sends a real backend request. The participant never needs to compose a URL, token, header or JSON body.
- Hints are optional and revealed one at a time. Start with a question about what the dossier reference controls, then suggest comparing references, then give a concrete test only if requested. Never load the solution automatically or guess the participant's hypothesis for them.
- Results lead with a short explanation such as access allowed or access refused and what that establishes. Technical details expand to the actual request, response and timestamp so the evidence remains inspectable.
- Evidence saving captures the real result with the participant's explanation. A plain-language note is useful; copying raw request text is optional.
- Explain each new term where it appears. A dossier is a saved profile, permission is who may open it and the collector is the mock feed carrying messages. Authentication means recognising an account; permission checking means deciding which records that account may read.
- Defence explains the difference between closing access to a dossier and stopping new messages. Codex and the blue defender perform the source repair. Codex then supplies the synthetic operator code for the participant's guided maintenance actions.
- Revocation and the final retest are browser actions against the backend. The outcome shows which checks passed, failed or remain incomplete, without requiring interpretation of status codes.
- Keep the watchtower atmosphere, but label actions by what they do. Keyboard access, readable text and text labels accompany colour-based results. Technical decoration must not obscure the next action.

These are release gates. Browser QA must exercise the full guided path, including saving a note, opening the permitted dossier, requesting a hint, submitting a numeric reference, saving evidence, entering the operator code, revoking the feed and reading a real retest. Record Codex's QA separately from Adrian's later participation.

## Guided investigation and agent work

Keep builder QA evidence separate from Adrian's mission evidence. Start a new mission run immediately before his session. Codex sets up the explicit training baseline and supplies the browser link and analyst account. Keep the player briefing spoiler-light. Optional progressive hints may appear in the browser; the full solution remains separate.

| Session time | Activity |
| --- | --- |
| 16:45–17:00 | Adrian compares the joke and slide, saves an observation and initial hypothesis, opens his permitted dossier and investigates the numeric reference with optional hints |
| 17:00–17:15 | Red scout proposes one scoped hypothesis; red validator independently reproduces the request and saves the response |
| 17:15–17:25 | Adrian saves the real result with a plain explanation, reviews independent evidence and distinguishes observation from inference |
| 17:25–17:40 | Blue defender proposes and applies one reviewed source patch; Adrian reviews the explanation, receives the operator code and uses guided controls to revoke the feed |
| 17:40–17:55 | Adrian triggers the browser retest and reads the outcome; red agents check the original and one related variant; permitted access and stopped collection are verified |

The main Codex session coordinates three specialists within four concurrent slots. The scout receives the player briefing, local address and analyst credential, without source or the solution. The validator receives the hypothesis and independently captures its own request and response. These are instruction-based constraints, not an enforced sandbox or a claim of blind assessment. The defender receives relevant source and logs and is the only patch writer during remediation.

Run one discovery/validation pass and one remediation/retest pass. Budget approximately 12 minutes of active specialist work for discovery/validation, 10 for the blue response and 8 for red retests, within the session windows above. Use the remaining session time for Adrian's investigation, review and guided actions. No recursive spawning or additional exploit chains. If another concern appears, record it for review without expanding the exercise.

Log each actual task's role, model when available, exact prompt, local target, start/end time, hypothesis or proposal, observed requests and responses, patch reference, verification and failures. Do not invent successful attempts, disagreements or dialogue. Deliver the exchange in an inspectable log; a replay interface is optional and can be omitted entirely.

## Verification and mission outcome

Use small integration checks against the running HTTP server and its real SQLite state. Use a temporary database and loopback port for automated checks. Pair these with an actual browser walkthrough. Avoid tests that merely inspect UI labels or mirror the implementation.

| Check | Required evidence |
| --- | --- |
| Authentication | Missing and invalid analyst credentials return `401`, including in vulnerable mode |
| Intended flaw | Valid analyst credential returns `200` with a restricted dossier in vulnerable mode |
| Original repair | The same analyst request returns `403` without dossier content in protected mode |
| Related variant | Requesting a second restricted dossier is also blocked after repair |
| Legitimate behaviour | Analyst's own dossier and filtered list still work; operator can perform maintenance |
| Control boundary | Analyst cannot read operator status or revoke the collector |
| Collection baseline | Valid integration credential accepts one synthetic event and increments the count |
| Containment | The same credential is rejected after revocation; count is unchanged and old records remain |
| Restart and reset | Revocation survives restart; reset restores documented fixtures while completed evidence files remain |
| Final packaging | Protected startup is the default; explicit training replay reproduces only the intended flaw |
| Browser and network | Three views work; requests use the local backend and assets; the listener is loopback only |
| Beginner journey | Browser-only observation, numeric dossier test, optional hints, evidence, operator code, revocation and real retest work with plain explanations |
| Outcome calculation | Success, false victory, failed defence and incomplete cases match STORY.md |

For each mission evidence item save the run ID, timestamp with timezone, source revision or hash, mode, synthetic actor, request, response and relevant before/after state. Record actual participant involvement. Hash the completed bundle for later comparison; do not describe hashes as proof that the fictional story is real.

An operator-triggered verification action runs the real probes and writes results bound to the current mission, code and state. The ending reads those results. A mode change, reset or later source change invalidates them until retested. The browser cannot award an ending by submitting its own pass/fail booleans.

Evaluate the conditions in STORY.md when the participant requests a final debrief. Missing participant evidence or steps not yet performed remain incomplete. For a completed verification attempt, broken legitimate behaviour or an ineffective repair yields The Raid Wipes and takes precedence over continued collection. A claimed victory with a repaired boundary but a newly accepted collection event yields The False Victory. Preserved evidence, blocked original and variant requests, rejected collection and working authorised access yield Victory With Loose Ends. Test these classifications in isolated fixtures without fabricating a failed live agent run. The paused sale is always a fictional epilogue.

Record a victory declaration only when Adrian or an agent actually makes one, through an explicit narrative action or a timestamped log entry before the collection retest. Keep that declaration separate from probe results. Continued collection without a premature victory claim means containment is incomplete and offers the revocation step. A debrief request alone is not a claim of victory.

## Scope cuts and hard checkpoints

| Trigger | Action |
| --- | --- |
| Backend misses 15:25 | Use up to 20 minutes of the UI budget; fall back to plain functional tabs |
| Visual work is unfinished at 16:00 | Freeze polish; finish the clue, dossiers, collector and request results |
| Required checks fail at 16:20 | Use the QA block for repairs; do not start Adrian's session with a broken fixture |
| Lab is not investigation-ready at 16:45 | Use the buffer for the blocker, reduce optional presentation and state the impact on the session |
| Specialist work reaches its cap | End exploration; complete one validated finding, one reviewed patch and the required retests |
| Session reaches 17:55 | Finish containment and retests before extending discussion; use the buffer only if essential steps remain |
| Report work reaches 18:35 | Keep concise Markdown and the four essential screenshots; omit PDF and replay UI |
| Fresh reproduction fails at 18:55 | Repair and repeat affected checks before publication |
| Publication is unverified at 19:20 | Delay archival and use the buffer to verify the repository and release |
| A required step remains at 20:00 | Record the exact incomplete state and continuation action; do not claim completion |

Keep one permission flaw, one collector, six dossiers, the three compact views, verified endings, the real agent log and Adrian's investigation. Cut animation, extra lore, sound, elaborate export formats and interface replay before reducing verification.

## Final files and GitHub sequence

The proposed source layout is intentionally small:

```text
server.py                    HTTP routes and launch/reset commands
lab/                         Storage, authorisation and fixture loading
fixtures/                    Synthetic story and seed data
web/                         One page, shared CSS/JS and local SVG
tests/                       HTTP behaviour and outcome checks
docs/                        Plans, briefing, solution and report
evidence/                    Reviewed request/response bundle and patch
screenshots/                 Four inspected images
var/                         Ignored runtime database and temporary files
README.md                    Verified setup, results, attribution and limits
LICENSE                      Proposed MIT licence, included in release review
.gitignore                   Runtime files, caches and private review notes
```

Use a short report covering the mission, Adrian's observations, confirmed finding, repair, containment, retests, limitations and assistance. Use direct evidence links. The README explains protected startup, deliberate training replay and reset. Describe the result as a guided educational project rather than professional red-team certification or production security. Runtime databases and real account credentials are excluded; published mock credentials are clearly identified as synthetic.

1. Check the authenticated GitHub owner and availability of `raid-the-watchtower` early, without creating a remote repository. Put the verified owner, intended public visibility and any naming conflict in the local review notes. Do not overwrite an existing repository.
2. Finish the code, report, source attribution, licence, screenshots and release notes. Inspect the staged content and run the documented commands from a clean local copy without the existing runtime database. Preserve the completed mission evidence separately. Repeat affected checks after any repair.
3. Present the exact repository owner/name, visibility, files, licence and v1.0 notes for Adrian's publication approval. The existing project plan requires explicit approval before pushing or publishing. Obtain it against these concrete contents, then publish the repository and release as approved.
4. Verify the actual remote files, default branch, commit, v1.0 tag and published release. Complete README metadata and resolve any open project issues or pull requests before archival. Do not create tracking issues merely to close them.
5. Present the verified release for Adrian's archival approval, then archive and verify the repository's actual archived flag and visible state. Save a local completion receipt with repository/release links, commit/tag, archive verification time and local reproduction result. This receipt is kept locally because the remote is read-only after archival.

GitHub archival makes the repository read-only and indicates that it is no longer actively maintained, so publish and verify the release first. The README and release notes explain that this educational project is complete. See [GitHub's archival documentation](https://docs.github.com/en/repositories/archiving-a-github-repository/archiving-repositories).

The build can finish today if it starts near the scheduled time, the required gates pass and Adrian is available for the final reviews. The schedule is a working budget, not a guarantee. Preserve the evidence and report the real state if timing or verification blocks the full finish.
