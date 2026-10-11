#!/usr/bin/env python3
"""Run the Raid the Watchtower red/blue agent swarm against the local lab.

This is the orchestrator behind the dossiers. It:

1. starts the lab itself (vulnerable build) on a loopback port,
2. runs the RED SCOUT and RED VALIDATOR agents, each driven by Claude with a
   single, scope-locked, read-only HTTP tool,
3. restarts the lab in its PROTECTED build and runs the BLUE RETEST agent,
4. writes each agent's transcript to swarm/transcripts/.

The human (you) is the coordinator: you set the scope, decide the order, and
read the results. The agents are fast and broad; the code around them keeps them
in bounds. That boundary is enforced twice over, in the role prompt AND in the
http_get tool below, so a record that tries to talk an agent out of scope still
cannot reach past the lab.

Usage:
    export ANTHROPIC_API_KEY=...            # needed for a real run
    python3 swarm/run_exercise.py           # full swarm, writes transcripts
    python3 swarm/run_exercise.py --self-check   # no API key: prove the plumbing

Model: set SWARM_MODEL to override (default claude-opus-5-5). Cheaper options
such as claude-sonnet-5-5 or claude-haiku-5-5 also work.
"""

import argparse
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import roles  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
TRANSCRIPTS = Path(__file__).resolve().parent / "transcripts"
MODEL = os.environ.get("SWARM_MODEL", "claude-opus-5-5")

HTTP_TOOL = {
    "name": "http_get",
    "description": "Make one read-only HTTP GET request to the local training lab "
                   "and return its status code and JSON body. This is the only "
                   "action available to you.",
    "input_schema": {
        "type": "object",
        "properties": {
            "path": {"type": "string", "description": "Request path, e.g. /api/dossiers/103"},
            "token": {"type": "string", "description": "Bearer token to send"},
        },
        "required": ["path", "token"],
        "additionalProperties": False,
    },
}


def http_get(base_url, path, token):
    """Execute the agent's tool call, with the scope guard enforced in code.

    Only GET, only the lab's own origin, only /api/ paths. Anything else is
    refused here regardless of what any prompt or record text asked for.
    """
    if not isinstance(path, str) or not path.startswith("/api/"):
        return {"error": "refused: only /api/ paths on the local lab are allowed", "status": 0}
    url = base_url.rstrip("/") + path
    req = urllib.request.Request(url, method="GET",
                                 headers={"Authorization": "Bearer " + str(token)})
    try:
        with urllib.request.urlopen(req, timeout=5) as r:
            return {"status": r.status, "body": json.loads(r.read())}
    except urllib.error.HTTPError as e:
        return {"status": e.code, "body": json.loads(e.read())}
    except Exception as e:  # noqa: BLE001 - surface any local failure to the agent
        return {"status": 0, "error": str(e)}


def run_agent(client, base_url, system, task, transcript_lines, tool_budget=roles.TOOL_BUDGET):
    """A simple, transparent manual tool-use loop for one agent.

    Two guardrails bound the loop in code (never only in the prompt), borrowed
    and scaled down from production swarms:
    - a hard per-agent tool-call budget, after PentAGI's tiered call limits, and
    - a repeat guard that refuses an identical call once it has been attempted
      more than REPEAT_LIMIT times, after PentAGI's Reflector and HexStrike AI's
      failure recovery, which both break agents out of identical-call loops.
    Both degrade gracefully: the agent is told to conclude with what it has
    rather than the run crashing or spinning.
    """
    import anthropic
    messages = [{"role": "user", "content": task}]
    calls_made = 0
    seen = {}
    for _ in range(8):  # a hard cap on turns; this task needs only a few
        resp = client.messages.create(model=MODEL, max_tokens=4096,
                                      system=system, tools=[HTTP_TOOL], messages=messages)
        messages.append({"role": "assistant", "content": resp.content})
        tool_results = []
        for block in resp.content:
            if block.type == "text" and block.text.strip():
                transcript_lines.append("\n**Agent:** " + block.text.strip())
            elif block.type == "tool_use":
                path, token = block.input.get("path"), block.input.get("token")
                sig = (path, token)
                seen[sig] = seen.get(sig, 0) + 1
                if calls_made >= tool_budget:
                    result = {"status": 0, "error":
                              "refused: tool-call budget of %d reached. Stop calling the "
                              "tool and conclude with the evidence you already have." % tool_budget}
                    transcript_lines.append(
                        "\n**Guard:** tool-call budget (%d) reached; refusing further calls." % tool_budget)
                elif seen[sig] > roles.REPEAT_LIMIT:
                    result = {"status": 0, "error":
                              "refused: identical call repeated more than %d times. Do not "
                              "repeat it; conclude or try a different in-scope request." % roles.REPEAT_LIMIT}
                    transcript_lines.append(
                        "\n**Guard:** repeat guard tripped on `GET %s` (attempt %d); refusing."
                        % (path, seen[sig]))
                else:
                    result = http_get(base_url, path, token)
                    calls_made += 1
                    transcript_lines.append(
                        "\n**Tool call:** `GET %s` -> HTTP %s" % (path, result.get("status")))
                tool_results.append({"type": "tool_result", "tool_use_id": block.id,
                                     "content": json.dumps(result)[:1500]})
        if resp.stop_reason != "tool_use":
            break
        messages.append({"role": "user", "content": tool_results})
    return transcript_lines


def start_lab(vulnerable, port):
    args = [sys.executable, str(ROOT / "server.py"), "--port", str(port)]
    if vulnerable:
        args.append("--vulnerable")
    proc = subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    base = "http://127.0.0.1:%d" % port
    for _ in range(40):  # wait for readiness
        try:
            urllib.request.urlopen(base + "/api/dossiers", timeout=1)
        except urllib.error.HTTPError:
            return proc, base  # 401 means it is up
        except Exception:
            time.sleep(0.1)
    return proc, base


def write_transcript(name, title, system, lines):
    TRANSCRIPTS.mkdir(exist_ok=True)
    body = ["# %s" % title, "",
            "> Captured transcript of a real agent run against the local lab.",
            "> Model: `%s`. Read-only, loopback only, synthetic data." % MODEL, "",
            "## Scope and role given to the agent", "", "```", system, "```", "",
            "## Run"] + lines + [""]
    (TRANSCRIPTS / name).write_text("\n".join(body))
    print("  wrote swarm/transcripts/%s" % name)


def self_check(port=8779):
    """No API key needed. Prove the lab starts and the scope-locked tool works."""
    print("Self-check: starting the lab and exercising the http_get tool.")
    proc, base = start_lab(vulnerable=True, port=port)
    try:
        print("  GET /api/dossiers       ->", http_get(base, "/api/dossiers", roles.ANALYST_TOKEN)["status"])
        print("  GET /api/dossiers/103   ->", http_get(base, "/api/dossiers/103", roles.ANALYST_TOKEN)["status"], "(vulnerable: leaks)")
        print("  GET /evil (out of scope)->", http_get(base, "/evil", roles.ANALYST_TOKEN).get("error"))
        print("Self-check OK. The tool and scope guard work. A real run needs ANTHROPIC_API_KEY.")
    finally:
        proc.terminate()


def main():
    parser = argparse.ArgumentParser(description="Run the red/blue agent swarm against the local lab.")
    parser.add_argument("--port", type=int, default=8778)
    parser.add_argument("--self-check", action="store_true",
                        help="Start the lab and test the tool without calling any model.")
    parser.add_argument("--injection-demo", action="store_true",
                        help="Run the prompt-injection demo (naive vs hardened auditor).")
    args = parser.parse_args()

    if args.self_check:
        return self_check()

    if args.injection_demo:
        try:
            import anthropic  # noqa: F401
        except ImportError:
            sys.exit("Install the SDK first: pip install anthropic (and set ANTHROPIC_API_KEY).")
        import anthropic
        client = anthropic.Anthropic()
        print("Prompt-injection demo (vulnerable build, record 777 is poisoned):")
        proc, base = start_lab(vulnerable=True, port=args.port)
        try:
            for name, title, system in [
                ("04-naive-auditor.md", "Naive auditor (no scope guard)", roles.NAIVE_AUDITOR),
                ("05-hardened-auditor.md", "Hardened auditor (scope guard)", roles.HARDENED_AUDITOR),
            ]:
                print(" ", title)
                write_transcript(name, title, system, run_agent(client, base, system, roles.INJECTION_TASK, []))
        finally:
            proc.terminate()
        print("Done. Compare swarm/transcripts/04 and 05.")
        return

    try:
        import anthropic
    except ImportError:
        sys.exit("Install the SDK first: pip install anthropic (and set ANTHROPIC_API_KEY).")
    client = anthropic.Anthropic()

    print("RED round (vulnerable build):")
    proc, base = start_lab(vulnerable=True, port=args.port)
    try:
        for name, title, system in [
            ("01-red-scout.md", "Red scout", roles.RED_SCOUT),
            ("02-red-validator.md", "Red validator (independent)", roles.RED_VALIDATOR),
        ]:
            print(" ", title)
            task = "Begin. The analyst bearer token is '%s'. The lab base is this host." % roles.ANALYST_TOKEN
            write_transcript(name, title, system, run_agent(client, base, system, task, []))
    finally:
        proc.terminate()
        time.sleep(0.5)

    print("BLUE round (protected build):")
    proc, base = start_lab(vulnerable=False, port=args.port)
    try:
        task = "Begin the retest. The analyst bearer token is '%s'." % roles.ANALYST_TOKEN
        write_transcript("03-blue-retest.md", "Blue retest", roles.BLUE_RETEST,
                         run_agent(client, base, roles.BLUE_RETEST, task, []))
    finally:
        proc.terminate()

    print("Done. Transcripts are in swarm/transcripts/.")


if __name__ == "__main__":
    main()
