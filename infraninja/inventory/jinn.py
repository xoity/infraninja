# inventory || jinn.py

import os
import logging
import requests
from typing import Dict, Any, List, Tuple
from pathlib import Path
from infraninja.utils.motd import show_motd

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
)
logger = logging.getLogger(__name__)

show_motd()

INVENTORY_ENDPOINT = "/inventory/servers/"
EXCLUDED_FILES = {"config", "known_hosts", "authorized_keys", "environment"}


def get_groups_from_data(data):
    """Extract unique groups from server data."""
    groups = set()
    for server in data.get("result", []):
        if server.get("group", {}).get("name_en"):
            groups.add(server["group"]["name_en"])
    return sorted(list(groups))


def get_ssh_key(server_data: dict) -> str:
    """Dynamically find all possible SSH keys in ~/.ssh"""
    # 1. Check if key is specified in server data
    if server_data.get("ssh_key"):
        expanded_key = os.path.expanduser(server_data["ssh_key"])
        if os.path.exists(expanded_key):
            return expanded_key

    # 2. Check for project-specific keys
    key_dir = Path.home() / ".ssh" / "keys"
    project_keys = []
    if key_dir.exists():
        for key_file in key_dir.glob(f"{server_data['hostname']}*"):
            if key_file.is_file() and key_file.stat().st_mode & 0o400:
                project_keys.append(str(key_file))

    # 3. Find all potential keys in ~/.ssh
    ssh_dir = Path.home() / ".ssh"
    system_keys = []
    for key_file in ssh_dir.iterdir():
        if (
            key_file.is_file()
            and not key_file.name.endswith(".pub")
            and key_file.name not in EXCLUDED_FILES
            and key_file.stat().st_mode & 0o400
        ):
            system_keys.append(str(key_file))

    # Combine and deduplicate keys
    found_keys = list(set(project_keys + system_keys))

    # 4. Handle key selection
    if len(found_keys) > 1:
        logger.info("\nDiscovered SSH keys:")
        for i, key in enumerate(found_keys, 1):
            logger.info(f"{i}. {key}")
        while True:
            choice = input("Select key to use (number) or 'cancel' to abort: ").strip()
            if choice.lower() == "cancel":
                raise ValueError("SSH key selection cancelled")
            try:
                selected = found_keys[int(choice) - 1]
                if not os.path.isfile(selected):
                    raise ValueError("Selected path is not a file")
                return selected
            except (ValueError, IndexError):
                logger.warning("Invalid selection, please try again")

    if found_keys:
        return found_keys[0]

    raise FileNotFoundError("No valid SSH keys found in ~/.ssh")


def configure_ssh_settings(server: dict) -> dict:
    """Configure SSH settings including bastion proxy."""
    config = {}

    # Bastion configuration
    if server.get("bastion"):
        bastion = server["bastion"]
        proxy_command = (
            f"ssh -W %h:%p -p {bastion.get('port', 22)} "
            f"{bastion['ssh_user']}@{bastion['hostname']}"
        )
        config.update({"_ssh_proxy_command": proxy_command, "_ssh_forward_agent": True})

    # SSH key configuration
    try:
        config["ssh_key"] = get_ssh_key(server)
    except Exception as e:
        logger.error(f"SSH key error for {server['hostname']}: {str(e)}")
        raise

    # Port configuration
    if server.get("ssh_port"):
        config["ssh_port"] = server["ssh_port"]

    return config


def fetch_servers(
    access_key: str, base_url: str, selected_group: str = None
) -> List[Tuple[str, Dict[str, Any]]]:
    try:
        # API call for servers
        headers = {"Authentication": access_key}
        response = requests.get(
            f"{base_url.rstrip('/')}{INVENTORY_ENDPOINT}", headers=headers, timeout=10
        )
        response.raise_for_status()
        data = response.json()

        # Get groups
        groups = get_groups_from_data(data)
        if not groups:
            logger.error("No groups found in API response")
            return []

        # Group selection logic
        logger.info("\nAvailable groups:")
        for i, group in enumerate(groups, 1):
            logger.info(f"{i}. {group}")

        selected_groups = [selected_group] if selected_group else []
        if not selected_groups:
            while True:
                choice = input(
                    "\nEnter group numbers (space-separated) or '*' for all groups: "
                ).strip()
                if choice == "*" or choice == "":
                    selected_groups = groups
                    break
                try:
                    choices = [int(x) for x in choice.split()]
                    if all(1 <= x <= len(groups) for x in choices):
                        selected_groups = [groups[i - 1] for i in choices]
                        break
                    logger.warning("Invalid choice. Please select valid numbers.")
                except ValueError:
                    logger.warning("Please enter valid numbers or '*'.")

        logger.info("\nSelected groups: %s", ", ".join(selected_groups))

        show_motd(selected_groups=selected_groups)

        # Build host list
        hosts = []
        for server in data.get("result", []):
            try:
                if not all(
                    [
                        server.get("group", {}).get("name_en") in selected_groups,
                        server.get("is_active", False),
                        server.get("hostname"),
                    ]
                ):
                    continue

                ssh_config = configure_ssh_settings(server)

                hosts.append(
                    (
                        server["hostname"],
                        {
                            "ssh_user": server.get("ssh_user"),
                            "ssh_key": ssh_config["ssh_key"],
                            "_ssh_proxy_command": ssh_config.get("_ssh_proxy_command"),
                            "ssh_port": server.get("ssh_port", 22),
                            **server.get("attributes", {}),
                        },
                    )
                )

            except KeyError as e:
                logger.error(f"Skipping server due to missing key: {str(e)}")
                continue
            except Exception as e:
                logger.error(f"Skipping {server.get('hostname')}: {str(e)}")
                continue

        return hosts

    except requests.exceptions.RequestException as e:
        logger.error(f"API request failed: {str(e)}")
        return []
    except Exception as e:
        logger.error(f"Critical error: {str(e)}")
        return []


access_key = input("Please enter your access key: ")
base_url = input("Please enter the Jinn API base URL: ")
hosts = fetch_servers(access_key, base_url)

if not hosts:
    logger.error("No valid hosts found. Check the API response and try again.")
else:
    logger.info("\nSelected servers:")
    for hostname, attrs in hosts:
        logger.info("- %s (User: %s)", hostname, attrs["ssh_user"])
