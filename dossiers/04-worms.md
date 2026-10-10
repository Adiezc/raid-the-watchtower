# Dossier 04 — Worms (malware that spreads itself)

> **Illustrative, not run.** This threat is analysed, not executed — a safe, synthetic red/blue study set in the fictional world. No working attack material. The one *runnable* flaw in this project is [dossier 01](01-broken-access-control.md).

**Threat class:** Self-propagating malware (network/community worm)
**In one line:** A worm is malware that copies itself from one victim to the next with no one having to click anything.

## Story hook
A NextVoice member uploads a shiny new combat-UI mod to the "NextVoice Nightwatch" guild chat. It works — but quietly, the moment it loads, it re-posts itself to every other member's add-on folder and pushes copies into their chats too. By morning half the guild is "sharing" it without ever choosing to. Rumour says Gallantir seeded the first copy.

## 🔴 Red — how the attack works
What makes something a *worm* rather than ordinary malware is **self-propagation**: it carries its own spreading logic and does not wait for a human to be tricked a second time. Install it once and it reaches for the next host on its own.

To spread, a worm needs a way to find and reach new hosts. In our story the "network" is the community itself: the mod reads the guild roster and member list, then uses the chat's own share/auto-sync feature to deliver a copy to each contact. Real worms do the equivalent on computer networks — scanning for reachable machines and slipping in through an unpatched flaw or an open, trusting channel.

**Speed is the whole point.** Each new victim becomes a new sender, so the count doubles and doubles again. A worm can blanket a community in minutes, long before a human notices. Historically this is why worms like Morris (1988), Code Red and SQL Slammer (2001–2003), and later WannaCry (2017) caused outsized damage — they moved faster than people could react, and WannaCry's spread was stopped largely by a patch that was already available but unapplied.

The copying is the threat by itself (clogged channels, crashes), but a worm can also carry a **payload** — anything from stealing data to installing a backdoor. The spreading and the payload are separate parts: you can understand one without the other, and no attack code is needed here to see the shape.

## 🔵 Blue — how you see it and stop it
- **Patch and update promptly.** Worms ride known, unpatched holes. Keeping the game client, chat app and add-on loader current removes the doors they walk through.
- **Segment the network / community.** Don't let one compromised member reach everyone. Separate channels, permission tiers and sub-guilds act as firebreaks.
- **Disable auto-run and auto-share.** If mods don't execute or re-share on their own, the chain cannot self-propagate.
- **Watch for anomalous spread.** The same file appearing everywhere at once, or one account suddenly messaging the whole roster, is the signature. Rate limits and alerts catch it.
- **Isolate fast; have a kill-switch.** Quarantine affected accounts, pause the share feature, revoke the offending upload. Containing the spread beats cleaning each victim.
- **Keep clean backups.** So you can restore without negotiating with whatever the payload did.

## ⚠️ Honest note
This is an analysis, not a live demo — nothing here propagates. It shows the *pattern* of self-spread and the defences that blunt it; it does not prove any specific system is vulnerable, and it reproduces no exploit. Worms are uniquely dangerous because spread is automatic and exponential: by the time you see patient zero, there are thousands. That is exactly why containment (cut the spread) matters more than cure (clean each host) — you are racing a doubling clock.

## Fundamentals (the takeaway)
- **Worm vs trojan:** a trojan ([dossier 03](03-trojans.md)) needs a victim to be tricked into running it *each time*; a worm tricks (or exploits) once, then spreads itself with no further human action.
- **Spread is the superpower and the weakness:** the same automatic copying that makes worms fast also makes them noisy — unusual, mass, self-initiated activity is detectable and stoppable.
- **Defence is mostly preparation:** patch early, segment, disable auto-execute/auto-share, and rehearse rapid isolation — so the doubling clock never gets started.
