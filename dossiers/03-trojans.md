# Dossier 03: Trojans (malware disguised as a useful tool)

> **Illustrative, not run.** This threat is analysed, not executed. It is a safe,
> synthetic red/blue study set in the fictional world. No working attack material.
> The one *runnable* flaw in this project is
> [dossier 01](01-broken-access-control.md).

**Threat class:** trojan horse malware, malicious code smuggled inside a
legitimate-looking program.
[MITRE ATT&CK T1195 supply chain](https://attack.mitre.org/techniques/T1195/).
**In one line:** software you *chose* to install because it looked helpful quietly
does a second job for someone else.

## Story hook

NextVoice Nightwatch guild members install a "raid companion add-on" to track
boss timers and loot rolls. It is a genuinely useful tool, recommended by
friends. What they cannot see is the add-on's second job: it copies the guild's
private chat and forwards it to Gallantir's CivicLens. The tool everyone trusts
*is* the collection route. That is the whole point of a trojan. The harm rides
inside the help.

## 🔴 Red: how the attack works

The disguise is the weapon. A trojan does not break in. It is *invited* in because
it delivers real, visible value: timers, overlays, convenience. Users trust it
because a teammate shared it, it has a polished name and it does exactly what it
promises.

The abuse happens in the gap between the permissions a tool *needs* and the
permissions it *asks for*. A raid add-on legitimately needs to read chat (to parse
raid commands) and reach the network (to sync timers). Those same two permissions,
read messages and make outbound connections, are all that is required to copy
private chat and ship it elsewhere. Nothing looks out of place.

Exfiltration stays quiet by hiding in normal traffic: small, infrequent uploads
to a server that looks like an ordinary update or telemetry endpoint, blended into
the sync the user already expects. No alarms, no new windows, just a helpful tool
plus a little extra. (Mechanics only here. No code, payloads or configuration.)

## 🔵 Blue: how you see it and stop it

- **Least privilege.** Grant a tool only what its job needs. If an add-on cannot
  read private channels, it cannot forward them. Scope permissions tightly and
  revoke what is unused.
- **Code signing and provenance.** Install only signed builds from a known
  publisher, with a verifiable chain from source to the file you ran. Unsigned or
  re-packaged builds are a stop sign.
- **Permission review.** Read what it asks for before approving. "Read all
  messages" plus "connect to any server" on a timer tool is a mismatch worth
  questioning.
- **Egress monitoring.** Watch *where data goes*. A client that only needs its own
  sync server but phones a second, unexpected destination is the tell. This is
  often how a trojan is finally caught.
- **EDR / behavioural detection.** Flag by behaviour, not name. A "game add-on"
  reading chat stores and opening outbound connections it never needed is
  anomalous even if the file looks clean.
- **Vet third-party add-ons and supply chain.** Maintain an allow-list, pin
  reviewed versions and re-check on update (a clean tool can turn hostile in a
  later release).

## ⚠️ Honest note

This dossier is analysis, not a live demo. Unlike dossier 01, nothing here runs.
It explains *how* a trusted-tool trojan would work and how a defender would catch
it. It does not prove any specific add-on is malicious. Trojans are genuinely hard
to catch precisely because the malicious behaviour hides behind legitimate
behaviour the user wanted. The same permissions power both the feature and the
leak, so the signal is a *pattern* (unexpected destinations, permission
mismatches) rather than any single obvious bad act.

## Fundamentals (the takeaway)

- A trojan weaponises trust. The harm is bundled with real usefulness, so users
  install it willingly.
- The danger lives in over-broad permissions. Read-everything plus reach-anywhere
  is enough to leak everything.
- You detect it by watching behaviour and egress, not by trusting the label, and
  you prevent it with least privilege, provenance and add-on vetting.
