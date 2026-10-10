# Dossier 05: DDoS (drowning a service in traffic)

> **Illustrative, not run.** This threat is analysed, not executed. It is a safe,
> synthetic red/blue study set in the fictional world. No working attack material.
> The one *runnable* flaw in this project is
> [dossier 01](01-broken-access-control.md).

**Threat class:** availability attack (distributed denial-of-service).
**In one line:** flood a website with so much junk traffic that real visitors
cannot get through.

## Story hook

Two days before NextVoice's procurement hearing, its campaign site slows to a
crawl, then stops answering at all. Supporters trying to read the youth-rights
brief see only a spinning loader. The arguments are still written. Nobody can
reach them. It is not a leak or a defacement. It is a crowd of fake visitors
jamming the doorway. Gallantir does not need to win the debate if the public never
sees it start.

## 🔴 Red: how the attack works

A denial-of-service attack does not break into anything. It exhausts something.
Every server has limits (bandwidth, connections, processing time), and the goal is
simply to use them all up so nothing is left for genuine users. There are three
broad flavours:

- **Volumetric.** Raw flood. Pure traffic volume fills the site's "pipe" the way a
  fire hose overwhelms a drinking straw.
- **Protocol.** Exploits the handshakes that start a connection, leaving the server
  holding thousands of half-open conversations that never complete.
- **Application-layer (L7).** Fewer, cleverer requests that each cost the server
  real work (the expensive search page, the report generator), so a trickle does
  the damage of a flood.

The "distributed" part is what makes it hard to stop. Instead of one source you
can simply block, the traffic comes from thousands of scattered machines at once,
often ordinary devices quietly conscripted into a *botnet* without their owners'
knowledge. Attackers can also use **amplification**: sending small forged requests
to misconfigured public servers that reply with much larger responses aimed at the
victim, turning a little effort into a lot of traffic. The result looks, at a
glance, like a sudden wave of popularity, which is exactly the problem.

## 🔵 Blue: how you see it and stop it

Defence is about absorbing, filtering and spreading load so no single point drowns:

- **CDN and anycast.** Sit the site behind a global network that copies content to
  many locations, so attack traffic is spread across huge capacity instead of
  hitting one server.
- **Upstream scrubbing.** Providers "clean" traffic far from your server, dropping
  the obvious junk before it ever arrives.
- **Rate limiting and caching.** Cap how often any one source can hit expensive
  endpoints. Serve cached copies so most requests never touch the application.
- **Autoscaling.** Add capacity automatically under load (within a budget. Scaling
  is not free).
- **WAF for L7.** A web application firewall spots and blocks malicious request
  patterns that mimic real users.
- **Anomaly detection and a playbook.** Baseline normal traffic so spikes stand
  out, with a rehearsed incident plan: who to call, which provider toggles to
  flip, how to post a status page.

## ⚠️ Honest note

This dossier is analysis, not a live demo. Nothing here floods anything. It shows
what the attack *is* and how defenders respond. It does not prove any particular
site's capacity. Crucially, a large volumetric attack can exceed everything a
single victim owns. You cannot absorb more traffic than your connection can
physically carry, so real defence depends on upstream providers and CDNs with far
bigger pipes. Availability is a shared responsibility, not a solo fix.

## Fundamentals (the takeaway)

- DDoS attacks **availability**, not secrets. The aim is to silence, not to steal.
- "Distributed" is the hard part. Many sources mean you cannot just block one
  address.
- Resilience is bought **before** the attack: capacity, caching and provider help
  arranged in advance, not improvised under fire.
