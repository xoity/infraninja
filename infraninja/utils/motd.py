import json
from datetime import datetime
from pathlib import Path
import os
from typing import List, Optional

# Constants
HISTORY_FILE = Path.home() / ".infraninja" / "history.json"
MOTD_FILE = "/etc/motd"
MAX_HISTORY = 5



class InfraNinjaHistory:
    DEFAULT_DATA = {
        "last_access": None,
        "selected_groups": [],
        "server_history": [],
        "deploy_history": [],
    }

    def __init__(self):
        self.history_file = HISTORY_FILE
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        self.data = self.DEFAULT_DATA.copy()
        self.load_history()

    def load_history(self):
        try:
            if self.history_file.exists():
                with open(self.history_file, "r") as f:
                    loaded_data = json.load(f)
                    # Update default data with loaded data
                    self.data.update(loaded_data)
        except Exception:
            pass  # Keep using default data if loading fails

    def save(self):
        try:
            with open(self.history_file, "w") as f:
                json.dump(self.data, f)
        except Exception:
            pass

    def update_access(self, groups: Optional[List[str]] = None):
        self.data["last_access"] = datetime.now().isoformat()
        if groups:
            self.data["selected_groups"] = groups
        self.save()

    def add_servers(self, servers: List[tuple]):
        """Add servers from jinn inventory"""
        for hostname, attrs in servers:
            entry = {
                "timestamp": datetime.now().isoformat(),
                "hostname": hostname,
                "group": attrs.get("group_name", "unknown"),
            }
            self.data["server_history"].insert(0, entry)
        self.data["server_history"] = self.data["server_history"][:MAX_HISTORY]
        self.save()

    def add_deploy(self, name: str, status: str, servers: List[str]):
        entry = {
            "timestamp": datetime.now().isoformat(),
            "name": name,
            "status": status,
            "servers": servers,
        }
        self.data["deploy_history"].insert(0, entry)
        self.data["deploy_history"] = self.data["deploy_history"][:MAX_HISTORY]
        self.save()


def format_motd() -> str:
    history = InfraNinjaHistory()
    current_time = datetime.now()

    content = [
        "\n",
        "=" * 70,
        "🥷 InfraNinja System Management",
        "=" * 70,
        f"\nCurrent Time: {current_time.strftime('%Y-%m-%d %H:%M:%S')}",
    ]

    if history.data.get("last_access"):
        last_access = datetime.fromisoformat(history.data["last_access"])
        content.append(
            f"\nLast Jinn Access: {last_access.strftime('%Y-%m-%d %H:%M:%S')}"
        )

        if history.data.get("selected_groups"):
            content.append(
                f"Selected Groups: {', '.join(history.data['selected_groups'])}"
            )

    if history.data.get("server_history"):
        content.append("\nRecent Server Access:")
        for entry in history.data["server_history"]:
            timestamp = datetime.fromisoformat(entry["timestamp"]).strftime(
                "%Y-%m-%d %H:%M"
            )
            content.append(f"- {timestamp} | {entry['hostname']} ({entry['group']})")

    if history.data.get("deploy_history"):
        content.append("\nRecent Deployments:")
        for entry in history.data["deploy_history"]:
            timestamp = datetime.fromisoformat(entry["timestamp"]).strftime(
                "%Y-%m-%d %H:%M"
            )
            content.append(f"- {timestamp} | {entry['name']} | {entry['status']}")
            if entry.get("servers"):
                content.append(f"  Servers: {', '.join(entry['servers'])}")

    content.extend(["", "=" * 70])
    return "\n".join(content)


def update_motd():
    """Update system MOTD file"""
    if not os.access(MOTD_FILE, os.W_OK):
        return
    try:
        with open(MOTD_FILE, "w") as f:
            f.write(format_motd() + "\n")
    except Exception:
        pass


def show_motd(
    hostname: Optional[str] = None,
    group: Optional[str] = None,
    selected_groups: Optional[List[str]] = None,
    servers: Optional[List[tuple]] = None,
    deploy_name: Optional[str] = None,
    deploy_status: Optional[str] = None,
    deploy_servers: Optional[List[str]] = None,
):
    """Display and update MOTD with current session info"""
    history = InfraNinjaHistory()

    if selected_groups:
        history.update_access(selected_groups)
    if servers:
        history.add_servers(servers)
    if deploy_name and deploy_status and deploy_servers:
        history.add_deploy(deploy_name, deploy_status, deploy_servers)

    content = format_motd()
    update_motd()
    print(content)
