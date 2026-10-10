# Dossier 02 — Phishing (social-engineering credential theft)

> **Illustrative, not run.** This threat is analysed, not executed — a safe, synthetic red/blue study set in the fictional world. No working attack material. The one *runnable* flaw in this project is [dossier 01](01-broken-access-control.md).

**Threat class:** Social engineering — credential theft via deception ([OWASP](https://owasp.org/www-community/attacks/) class; a human-layer attack, not a software bug).
**In one line:** instead of breaking the lock, the attacker tricks a person into handing over the key.

## Story hook

Dossier 01 showed one route to the private guild message: a missing permission check on the server. But Gallantir never needed the server to be broken. If a single NextVoice Nightwatch member could be fooled into typing their guild password into the wrong box, the same private chats and unpublished hearing arguments would walk out the front door — logged in, looking legitimate. Phishing is the plausible human-shaped alternative to the machine-shaped leak.

## 🔴 Red — how the attack works

Conceptually, the attack moves through four stages. No templates or code appear here; the point is to recognise the shape.

1. **Pretext** — the attacker studies public signals (a guild roster, a Discord handle, a recruiting post) and invents a believable reason to make contact: a "guild account verification," a "moderator action," a "hearing-document share."
2. **Lure** — a message arrives through a channel the target trusts (email, a DM, a chat link), carrying urgency and a single call to action: *click here, sign in now, or lose access.*
3. **Credential capture** — the link leads to a page that *looks* like the real login. Whatever the victim types is captured by the attacker, not the real service. Increasingly, attackers also relay the login live to defeat one-time codes.
4. **Use** — with working credentials, the attacker signs in as the member and reads exactly what that member could read — quietly, from a normal-looking session.

The target is the *person*, so no software patch alone closes it.

## 🔵 Blue — how you see it and stop it

- **Phishing-resistant MFA.** Passkeys or hardware security keys bind the login to the real site's identity, so a captured password alone is useless and relayed logins fail.
- **Email authentication.** Publish and enforce SPF, DKIM, and DMARC so spoofed "from NextVoice" mail is rejected or quarantined before anyone sees it.
- **Link and sender inspection.** Teach members to check the real destination, not the display text, and to be suspicious of look-alike domains and urgency.
- **A one-click report path.** Make reporting a suspected lure faster than complying with it; every report sharpens detection.
- **Detection signals.** Watch for impossible-travel logins, new-device sign-ins, a surge of password resets, or mail to many members pointing at one freshly registered domain.

## ⚠️ Honest note

This dossier is analysis, not a live demo — nothing here was sent, clicked, or captured. It proves the *mechanism* is plausible and that the defences are real and standard; it does not prove any NextVoice member was actually phished. Phishing stays hard to fully stop because it exploits trust and habit, not a flaw you can patch once. The goal is not zero clicks — it is making one click survivable: strong authentication, fast reporting, and layered detection so a single mistake is not a breach.

## Fundamentals (the takeaway)

- **Authenticating a login is not trusting the human behind it** — assume credentials can be stolen and make the stolen ones worthless (passkeys, hardware keys).
- **Verify the channel, not just the message** — check the real sender and the real destination before acting; urgency is a pressure tactic, not evidence.
- **Make reporting effortless and recovery fast** — the strongest control is a culture where a mistaken click is reported in seconds, not hidden.
