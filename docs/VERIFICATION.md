# Verification record

## Vulnerable baseline

Checked on 10 October 2026. Baseline commit: `f26be62`.

Command: `python3 -m unittest discover -s tests -v`.

Result: Nine HTTP integration checks against temporary SQLite databases and one isolated outcome classification check passed. A coordinator rerun completed successfully in 5.323 seconds.

The checks establish:

- The analyst list contains only its permitted records.
- The intentional detail-route flaw exposes restricted records to the authenticated analyst.
- Missing, invalid and wrong-purpose credentials are rejected.
- Analyst credentials cannot perform responder controls.
- The mock feed accepts only the supplied invented message with its separate credential.
- Revocation rejects later events without changing the stored count, and persists across restart.
- Evidence comes from actual recorded responses and survives reset.
- Optional hints are recorded as assistance.
- Real verification requests expose the baseline's failed permission checks and keep its unfinished mission incomplete.
- Static routes and local request restrictions behave as documented.

Isolated outcome checks exercise all three fictional endings. They do not represent an actual completed participant or agent exercise.

## Browser readiness

Completed on 10 October 2026 using a separate builder QA database at port 8766. These are implementation checks, not Adrian's investigation or red/blue results.

The coordinator used the real browser controls to compare the guild and slide, save explicitly labelled builder notes, save the clue, open an allowed record, request an unknown record and request the intended restricted record. The actual restricted response was saved as evidence. A hint was recorded. Wrong responder credentials were rejected and the supplied synthetic responder code unlocked the real controls. One synthetic event was accepted, then revocation rejected new collection while preserving two stored events. Real verification reported the baseline's two failed permission checks and an incomplete mission, without claiming that a repair had happened.

Reloading retained saved notes and evidence. Keyboard arrow navigation moved between the view tabs. Required instructions were measured at 14px and notebook introduction text at 13px. A 390 by 844 viewport exposed artwork overflow; the CSS was corrected and the recheck measured both viewport and document width at 390px. The temporary viewport override was reset. Desktop and narrow screenshots were visually inspected. Browser error and warning logs were empty after the final reload. JavaScript syntax passed `node --check web/app.js`.

An independent read-only review reran all ten tests successfully in 5.283 seconds. Its two interface findings were corrected: A failed or inconclusive event simulation cannot claim verified protection, and an empty mission clears old evidence rows and hint levels.

The fresh participant run is `run-2f9b7fa90656`, served at `http://127.0.0.1:8765/`. Its initial notebook and assistance list were empty and no verification had run when it was handed to Adrian. Builder QA was stopped. The starting screen is saved in `docs/screenshots/guild-start.jpg`.

## Interface redesign

Adrian requested a substantial visual redesign before starting his investigation. The landing-page structure was replaced with a guild client, corporate record console and defence terminal. Read-only review confirmed balanced HTML, unique IDs, complete accessibility references and preserved JavaScript selector contracts. Notes now precede clue testing in the mission log. Tab navigation supports Up/Down as well as Left/Right and adapts its accessibility orientation to the responsive layout.

The coordinator tested the redesign in a separate `var/ui-review.sqlite3` run at port 8766. Builder-labelled notes and the clue saved through actual controls; a permitted record opened with a visible, truthful `GET /api/dossiers/101 → HTTP 200` line, and its response saved. Reload retained the notes and two evidence items. The real responder controls ran all six checks and kept this unrepaired builder mission incomplete. These checks are not participant or red/blue results.

All three views were inspected at a 390 by 844 viewport without horizontal overflow. The desktop recheck also measured document width equal to the 1280px viewport. Message and note-input fonts measured 14px. Keyboard navigation selected the correct view and browser warning/error logs were empty. Temporary viewport overrides were reset. The refreshed participant client kept the original empty run and returned to Guild commons. Desktop screenshots of all three views and a full starting view were saved and inspected.

## Art and gradual introduction

The Frontend Design and imagegen skills informed the NextVoice Nightwatch pass. The original painted hall and local lantern, prism and case-file symbols were visually inspected. The only new server static route is an explicit image allowlist entry. The participant server was restarted with its existing database, preserving run `run-2f9b7fa90656` and its empty notes, evidence and assistance.

A separate `var/design-qa.sqlite3` run at port 8766 verified the initial conversation, slide-only opening, clue-triggered notes, saved-note-triggered record controls, an actual restricted response saved as evidence and the resulting responder invitation. Reload restored this progress. An unsaved note revision survived location changes. The narrow 390px viewport measured no horizontal overflow. Desktop screens were inspected and browser warnings/errors were empty. All automated baseline checks passed and JavaScript syntax passed. These are builder checks only.

## Participant and defensive verification

Not started. The actual source patch, agent requests, participant observations, containment and protected retests will be added after they occur.

## Final reproduction and publication

Not performed. No published release or archived repository is claimed.

## Classic dungeon art revision

The active hall asset was edited with imagegen to match the user's requested low-poly WoW Classic inspiration. Guild frames, bronze button fittings and angular character armour were updated. The live guild screen was visually inspected at desktop and 390px mobile sizes; the image loaded and document width matched the mobile viewport. JavaScript syntax and diff whitespace checks passed. This presentation-only revision did not change the server policy or participant data.


## Focused reading revision

The opening view now shows exactly one archived message, with previous/next controls and the slide action appearing on the final message. The visible checklist and persistent notebook were removed. A separate builder run `var/reading-qa.sqlite3` verified message progression, the slide action, clue save opening the dedicated notes screen, notes save returning to record tools and an actual permitted response replacing those tools. Record labels, additional record text and defence instructions are expandable.

Desktop and mobile screens were visually inspected. A mobile grid regression was corrected; the final 390px check measured a 358px main reading area and a 390px document, with one visible message. JavaScript syntax and whitespace checks passed. The participant run was not reset or used for builder evidence.


## History instead of side text

The persistent sidebars and header controls were consolidated into a native History & tools dialog. Only the current message and continuation remain on the opening screen. A separate builder run verified next-message progression, position/history surviving reload, rereading an earlier message and reopening the saved company slide after notes had been saved. The mobile recheck measured a 390px document and a 350px dialog within the 390px viewport. Temporary viewport overrides were reset and the QA server stopped. HTML structure, unique IDs, JavaScript syntax and whitespace checks passed.

## Protected build (after the repair)

Checked on 10 October 2026. Repair commit: `5546f6e`.

Command: `python3 -m unittest discover -s tests -v`.

Result: 13 checks pass (the 10 baseline checks plus 3 protected-mode checks) in about 6.9 seconds.

The protected-mode checks establish:

- The analyst reads only its own workspace files (101, 102) and is refused (HTTP 403) on every restricted file (103, 104, 105, 106).
- The operator still reads every workspace, so legitimate review is preserved.
- A missing file still returns 404, not 403, so the repair adds no new 403/404 oracle.
- The default startup (no flag) serves the protected, defended build.

An end-to-end run against the running protected build (real HTTP on 127.0.0.1:8765, fresh reset) confirmed authentication rejection, the full access boundary, operator review, collector acceptance before revocation and rejection after, the analyst role boundary on revocation, and all six mission verification checks passing. See `docs/AGENT-ROUND-LOG.md` for the recorded evidence.
