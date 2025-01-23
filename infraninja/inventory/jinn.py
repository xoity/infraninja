# inventory || jinn.py

import os
import logging
import requests
from typing import Dict, Any, List
from infraninja.utils.motd import show_motd
import getpass
from paramiko import RSAKey, PasswordRequiredException

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
)
logger = logging.getLogger(__name__)

show_motd(skip_initial=False)

INVENTORY_ENDPOINT = "/inventory/servers/"

def get_groups_from_data(data):
    """Extract unique groups from server data."""
    groups = set()
    for server in data.get("result", []):
        group = server.get("group", {}).get("name_en")
        if group:
            groups.add(group)
    return sorted(list(groups))

def fetch_servers(access_key: str, base_url: str, selected_group: str = None) -> List[Dict[str, Any]]:
    """Fetch servers and return structured inventory data."""
    try:
        headers = {"Authentication": access_key}
        response = requests.get(
            f"{base_url.rstrip('/')}{INVENTORY_ENDPOINT}",
            headers=headers
        )
        response.raise_for_status()
        data = response.json()

        groups = get_groups_from_data(data)
        logger.info("\nAvailable groups:")
        for i, group in enumerate(groups, 1):
            logger.info("%d. %s", i, group)

        if selected_group is None:
            while True:
                choice = input("\nEnter group numbers (space-separated) or '*' for all groups: ").strip()
                if choice == "*":
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
        else:
            selected_groups = [selected_group]

        inventory = []
        for server in data.get("result", []):
            if (server.get("group", {}).get("name_en") in selected_groups and 
                server.get("is_active", False)):
                
                bastion = server.get("bastion")
                server_data = {
                    "ssh_hostname": server["ssh_hostname"],
                    "ssh_user": server["ssh_user"],
                    "ssh_port": server["ssh_port"],
                    "group_name": server["group"]["name_en"],
                    "is_active": server.get("is_active", False),
                    "bastion": None
                }

                if bastion:
                    server_data["bastion"] = {
                        "hostname": bastion["hostname"],
                        "port": bastion["port"],
                        "ssh_user": bastion["ssh_user"]
                    }

                inventory.append(server_data)

        return inventory

    except requests.exceptions.RequestException as e:
        logger.error("Request error: %s", e)
        return []
    except Exception as e:
        logger.error("Unexpected error: %s", e)
        return []

# Get access key and API URL
access_key = input("Please enter your access key: ")
base_url = input("Please enter the Jinn API base URL: ")

# Check SSH key
key_path = os.path.expanduser("~/.ssh/id_rsa")
ssh_key_password = None

if os.path.exists(key_path):
    try:
        RSAKey.from_private_key_file(key_path)
        logger.info("\nSSH key is not encrypted.")
    except PasswordRequiredException:
        ssh_key_password = getpass.getpass("\nEnter passphrase for encrypted SSH key: ")
    except Exception as e:
        logger.error("Error loading SSH key: %s", e)
else:
    logger.warning("SSH key not found at %s", key_path)
    key_path = None

# Fetch hosts and format inventory for PyInfra
hosts = fetch_servers(access_key, base_url)

formatted_hosts = []
for server in hosts:
    bastion_config = {}
    if server["bastion"]:
        bastion_config = {
            "ssh_hostname": server["bastion"]["hostname"],
            "ssh_port": server["bastion"]["port"],
            "ssh_user": server["bastion"]["ssh_user"]
        }

    formatted_hosts.append((
        server["ssh_hostname"],
        {
            "ssh_user": server["ssh_user"],
            "ssh_key": key_path,
            "ssh_key_password": ssh_key_password,
            "ssh_port": server["ssh_port"],
            "bastion": bastion_config
        }
    ))

logger.info("\nSelected servers:")
for hostname, attrs in formatted_hosts:
    logger.info("- %s (User: %s)", hostname, attrs["ssh_user"])
    if attrs["bastion"]:
        logger.info("  ↳ Via bastion: %s:%d", 
                   attrs["bastion"]["ssh_hostname"], 
                   attrs["bastion"]["ssh_port"])
