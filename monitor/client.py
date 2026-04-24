#!/usr/bin/env python3
"""
Builder — Monitor Client

Helper functions for recording agent events to the monitor.
Can be used programmatically or via CLI.

CLI Usage:
    python3 client.py start --name "docs-builder" --desc "Building docs site"
    python3 client.py update <agent-id> --tool-calls 5 --activity "Write docs.html"
    python3 client.py complete <agent-id> --files "a.py,b.py"
    python3 client.py complete <agent-id> --status failed
    python3 client.py status
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError

DEFAULT_URL = "http://localhost:7865"


def api_call(method, path, data=None, base_url=DEFAULT_URL):
    """Make an API call to the monitor server."""
    url = f"{base_url}{path}"
    body = json.dumps(data).encode("utf-8") if data else None
    req = Request(url, data=body, method=method)
    req.add_header("Content-Type", "application/json")
    try:
        with urlopen(req) as resp:
            return json.loads(resp.read())
    except URLError as e:
        print(f"Error: Could not connect to monitor at {base_url}", file=sys.stderr)
        print(f"  Start the server with: python3 server.py", file=sys.stderr)
        sys.exit(1)


def start_agent(name, description="", agent_type="general-purpose", agent_id=None, base_url=DEFAULT_URL):
    """Record a new running agent."""
    data = {
        "name": name,
        "description": description,
        "agent_type": agent_type,
        "started_at": datetime.now().isoformat(),
    }
    if agent_id:
        data["id"] = agent_id
    return api_call("POST", "/api/agents", data, base_url)


def update_agent(agent_id, tool_calls=None, activity=None, files=None, base_url=DEFAULT_URL):
    """Update a running agent."""
    data = {}
    if tool_calls is not None:
        data["tool_calls"] = tool_calls
    if activity:
        data["activity"] = {"tool": activity.split(" ")[0], "detail": " ".join(activity.split(" ")[1:])}
    if files:
        data["files_changed"] = files
    return api_call("POST", f"/api/agents/{agent_id}/update", data, base_url)


def complete_agent(agent_id, status="completed", files=None, tool_calls=None, base_url=DEFAULT_URL):
    """Mark an agent as completed."""
    data = {"status": status}
    if files:
        data["files_changed"] = files
    if tool_calls is not None:
        data["tool_calls"] = tool_calls
    return api_call("POST", f"/api/agents/{agent_id}/complete", data, base_url)


def get_status(base_url=DEFAULT_URL):
    """Get current monitor status."""
    return api_call("GET", "/api/status", base_url=base_url)


def main():
    parser = argparse.ArgumentParser(description="Builder Monitor Client")
    parser.add_argument("--url", default=DEFAULT_URL, help=f"Monitor server URL (default: {DEFAULT_URL})")
    sub = parser.add_subparsers(dest="command", required=True)

    # start
    start_p = sub.add_parser("start", help="Record a new running agent")
    start_p.add_argument("--name", required=True, help="Agent name")
    start_p.add_argument("--desc", default="", help="Agent description")
    start_p.add_argument("--type", default="general-purpose", help="Agent type")
    start_p.add_argument("--id", default=None, help="Agent ID (auto-generated if omitted)")

    # update
    update_p = sub.add_parser("update", help="Update a running agent")
    update_p.add_argument("agent_id", help="Agent ID")
    update_p.add_argument("--tool-calls", type=int, help="Total tool calls so far")
    update_p.add_argument("--activity", help="Activity description (e.g. 'Write docs.html')")
    update_p.add_argument("--files", help="Comma-separated list of changed files")

    # complete
    complete_p = sub.add_parser("complete", help="Mark agent as completed")
    complete_p.add_argument("agent_id", help="Agent ID")
    complete_p.add_argument("--status", default="completed", choices=["completed", "failed", "cancelled"])
    complete_p.add_argument("--files", help="Comma-separated list of changed files")
    complete_p.add_argument("--tool-calls", type=int, help="Total tool calls")

    # status
    sub.add_parser("status", help="Show current status")

    args = parser.parse_args()

    if args.command == "start":
        result = start_agent(args.name, args.desc, args.type, args.id, args.url)
        print(json.dumps(result, indent=2))

    elif args.command == "update":
        files = args.files.split(",") if args.files else None
        result = update_agent(args.agent_id, args.tool_calls, args.activity, files, args.url)
        print(json.dumps(result, indent=2))

    elif args.command == "complete":
        files = args.files.split(",") if args.files else None
        result = complete_agent(args.agent_id, args.status, files, args.tool_calls, args.url)
        print(json.dumps(result, indent=2))

    elif args.command == "status":
        result = get_status(args.url)
        running = result.get("running", [])
        completed = result.get("completed", [])
        print(f"Running: {len(running)}  |  Completed today: {len(completed)}")
        for a in running:
            print(f"  {a['name']} ({a.get('agent_type', '?')}) — {a.get('tool_calls', 0)} tool calls")
        for a in completed:
            dur = a.get('duration_seconds', 0)
            m, s = divmod(int(dur), 60)
            print(f"  {a['name']} — {m}m{s}s — {a.get('status', '?')}")


if __name__ == "__main__":
    main()
