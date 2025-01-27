import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List

MOTD_FILE = os.path.join(str(Path.home()), ".infraninja_motd.json")

class MOTDManager:
    def __init__(self):
        self.motd_data = self._load_motd_data()

    def _load_motd_data(self) -> Dict:
        """Load MOTD data from file or create default structure."""
        try:
            if os.path.exists(MOTD_FILE):
                with open(MOTD_FILE, 'r') as f:
                    return json.load(f)
        except Exception:
            pass
        
        return {
            "last_run": None,
            "last_groups": [],
            "recent_servers": []
        }

    def _save_motd_data(self):
        """Save MOTD data to file."""
        try:
            with open(MOTD_FILE, 'w') as f:
                json.dump(self.motd_data, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save MOTD data: {e}")

    def update_access(self, groups: List[str], servers: List[str]):
        """Update MOTD with new access information."""
        self.motd_data["last_run"] = datetime.now().isoformat()
        self.motd_data["last_groups"] = groups
        
        # Keep only the 5 most recent servers
        current_servers = self.motd_data.get("recent_servers", [])
        updated_servers = servers + current_servers
        self.motd_data["recent_servers"] = list(dict.fromkeys(updated_servers))[:5]
        
        self._save_motd_data()

    def display_motd(self):
        """Display formatted MOTD information."""
        print("\n========= Welcome to InfraNinja =========")
        print(f"Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        if not self.motd_data["last_run"]:
            print("No previous access recorded.")
            print("=====================================\n")
            return

        last_run = datetime.fromisoformat(self.motd_data["last_run"])
        print(f"Last access: {last_run.strftime('%Y-%m-%d %H:%M:%S')}")
        
        if self.motd_data["last_groups"]:
            print("\nLast used groups:")
            for group in self.motd_data["last_groups"]:
                print(f"  - {group}")
        
        if self.motd_data["recent_servers"]:
            print("\nRecently accessed servers:")
            for server in self.motd_data["recent_servers"]:
                print(f"  - {server}")
        print("=====================================\n")

# Create global instance
motd = MOTDManager()
