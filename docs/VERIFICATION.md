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

## Participant and defensive verification

Not started. The actual source patch, agent requests, participant observations, containment and protected retests will be added after they occur.

## Final reproduction and publication

Not performed. No published release or archived repository is claimed.
