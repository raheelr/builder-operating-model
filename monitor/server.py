#!/usr/bin/env python3
"""
Builder — Live Agent Monitor Server

A lightweight HTTP server that serves the agent monitor dashboard
and exposes a JSON API backed by ~/.claude/monitor/status.json.

Usage:
    python3 server.py              # Start on default port 7865
    python3 server.py --port 8080  # Start on custom port
    python3 server.py --open       # Start and open browser

API:
    GET /              → Dashboard HTML
    GET /api/status    → Current status (running + completed + history)
    POST /api/agents   → Record a new agent event
    DELETE /api/agents/{id} → Remove an agent
"""

import argparse
import json
import os
import sys
import threading
import time
from datetime import datetime, date
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse

STATUS_DIR = Path.home() / ".claude" / "monitor"
STATUS_FILE = STATUS_DIR / "status.json"
HISTORY_FILE = STATUS_DIR / "history.json"
DASHBOARD_FILE = Path(__file__).parent / "dashboard.html"

# Lock for thread-safe file access
file_lock = threading.Lock()


def ensure_status_file():
    """Create the status file with default structure if it doesn't exist."""
    STATUS_DIR.mkdir(parents=True, exist_ok=True)
    if not STATUS_FILE.exists():
        write_status({"running": [], "completed": []})
    if not HISTORY_FILE.exists():
        write_history([])


def read_status():
    """Read the current status file."""
    try:
        with open(STATUS_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {"running": [], "completed": []}


def write_status(data):
    """Write to the status file atomically."""
    tmp = STATUS_FILE.with_suffix(".tmp")
    with open(tmp, "w") as f:
        json.dump(data, f, indent=2, default=str)
    tmp.rename(STATUS_FILE)


def read_history():
    """Read the history file."""
    try:
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []


def write_history(data):
    """Write to the history file atomically."""
    tmp = HISTORY_FILE.with_suffix(".tmp")
    with open(tmp, "w") as f:
        json.dump(data, f, indent=2, default=str)
    tmp.rename(HISTORY_FILE)


def get_full_status():
    """Build the full status response including history."""
    with file_lock:
        status = read_status()
        history = read_history()

    # Separate today's completed from history
    today = date.today().isoformat()
    today_completed = []
    for agent in status.get("completed", []):
        started = agent.get("started_at", "")
        if started.startswith(today):
            today_completed.append(agent)

    return {
        "running": status.get("running", []),
        "completed": today_completed,
        "history": history[-100:],  # last 100 history entries
        "timestamp": datetime.now().isoformat(),
    }


def record_agent_start(agent_data):
    """Record a new running agent."""
    with file_lock:
        status = read_status()
        agent = {
            "id": agent_data.get("id", f"agent-{int(time.time())}"),
            "name": agent_data.get("name", "unnamed"),
            "description": agent_data.get("description", ""),
            "agent_type": agent_data.get("agent_type", "general-purpose"),
            "started_at": agent_data.get("started_at", datetime.now().isoformat()),
            "status": "running",
            "tool_calls": 0,
            "recent_activity": [],
            "files_changed": [],
        }
        status["running"].append(agent)
        write_status(status)
    return agent


def record_agent_update(agent_id, update_data):
    """Update a running agent's status."""
    with file_lock:
        status = read_status()
        for agent in status["running"]:
            if agent["id"] == agent_id:
                if "tool_calls" in update_data:
                    agent["tool_calls"] = update_data["tool_calls"]
                if "activity" in update_data:
                    agent.setdefault("recent_activity", [])
                    agent["recent_activity"].append(update_data["activity"])
                    agent["recent_activity"] = agent["recent_activity"][-10:]
                if "files_changed" in update_data:
                    existing = set(agent.get("files_changed", []))
                    existing.update(update_data["files_changed"])
                    agent["files_changed"] = sorted(existing)
                break
        write_status(status)


def record_agent_complete(agent_id, result_data=None):
    """Move an agent from running to completed."""
    result_data = result_data or {}
    with file_lock:
        status = read_status()
        agent = None
        status["running"] = [
            a for a in status["running"]
            if a["id"] != agent_id or (agent := a) and False  # walrus-ish pop
        ]
        # Find the agent we removed
        if agent is None:
            # Try to find it — maybe the list comprehension trick didn't work
            for i, a in enumerate(status.get("running", [])):
                if a["id"] == agent_id:
                    agent = status["running"].pop(i)
                    break

        if agent:
            agent["status"] = result_data.get("status", "completed")
            agent["completed_at"] = datetime.now().isoformat()
            started = datetime.fromisoformat(agent["started_at"])
            agent["duration_seconds"] = (datetime.now() - started).total_seconds()
            if "files_changed" in result_data:
                agent["files_changed"] = result_data["files_changed"]
            if "tool_calls" in result_data:
                agent["tool_calls"] = result_data["tool_calls"]

            status.setdefault("completed", [])
            status["completed"].append(agent)

            # Also add to history
            history = read_history()
            history.append(agent)
            # Keep last 500 entries
            write_history(history[-500:])

        write_status(status)
    return agent


class MonitorHandler(SimpleHTTPRequestHandler):
    """HTTP handler for the monitor dashboard and API."""

    def log_message(self, format, *args):
        # Suppress default logging to keep terminal clean
        pass

    def send_json(self, data, status=200):
        body = json.dumps(data, indent=2, default=str).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")

        if path == "" or path == "/index.html":
            # Serve dashboard
            try:
                content = DASHBOARD_FILE.read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(content)))
                self.end_headers()
                self.wfile.write(content)
            except FileNotFoundError:
                self.send_error(404, "Dashboard HTML not found")
            return

        if path == "/api/status":
            self.send_json(get_full_status())
            return

        self.send_error(404)

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")

        content_length = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(content_length)) if content_length > 0 else {}

        if path == "/api/agents":
            agent = record_agent_start(body)
            self.send_json(agent, 201)
            return

        if path.startswith("/api/agents/") and path.endswith("/update"):
            agent_id = path.split("/")[3]
            record_agent_update(agent_id, body)
            self.send_json({"ok": True})
            return

        if path.startswith("/api/agents/") and path.endswith("/complete"):
            agent_id = path.split("/")[3]
            agent = record_agent_complete(agent_id, body)
            self.send_json(agent or {"error": "not found"}, 200 if agent else 404)
            return

        self.send_error(404)

    def do_DELETE(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")

        if path.startswith("/api/agents/"):
            agent_id = path.split("/")[3]
            record_agent_complete(agent_id, {"status": "cancelled"})
            self.send_json({"ok": True})
            return

        self.send_error(404)


def main():
    parser = argparse.ArgumentParser(description="Builder Live Agent Monitor")
    parser.add_argument("--port", type=int, default=7865, help="Port to serve on (default: 7865)")
    parser.add_argument("--open", action="store_true", help="Open browser on start")
    args = parser.parse_args()

    ensure_status_file()

    server = HTTPServer(("127.0.0.1", args.port), MonitorHandler)
    url = f"http://localhost:{args.port}"

    print(f"Builder — Live Agent Monitor")
    print(f"Dashboard: {url}")
    print(f"API:       {url}/api/status")
    print(f"Status:    {STATUS_FILE}")
    print()
    print("Press Ctrl+C to stop")

    if args.open:
        import webbrowser
        webbrowser.open(url)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down.")
        server.shutdown()


if __name__ == "__main__":
    main()
