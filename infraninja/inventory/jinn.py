# inventory || jinn.py

import os
import logging
import requests
from typing import Dict, Any, List, Tuple
from infraninja.utils.motd import show_motd
import getpass
from paramiko import RSAKey, PasswordRequiredException, SSHClient, AutoAddPolicy

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

def fetch_servers(access_key: str, base_url: str, selected_group: str = None) -> List[Tuple[str, Dict[str, Any]]]:
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

        hosts = []
        for server in data.get("result", []):
            if (server.get("group", {}).get("name_en") in selected_groups and 
                server.get("is_active", False)):
                
                bastion = server.get("bastion")
                host_data = {
                    **server.get("attributes", {}),
                    "ssh_user": server.get("ssh_user"),
                    "ssh_port": server.get("ssh_port", 22),
                    "is_active": server.get("is_active", False),
                    "group_name": server.get("group", {}).get("name_en"),
                    "bastion": None
                }

                if bastion:
                    host_data["bastion"] = {
                        "hostname": bastion["hostname"],
                        "port": bastion["port"],
                        "ssh_user": bastion["ssh_user"],
                        "ssh_key": key_path,
                        "ssh_key_password": ssh_key_password
                    }

                hosts.append((
                    server["ssh_hostname"],
                    host_data
                ))

        return hosts

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

# Fetch hosts and add connection parameters
hosts = fetch_servers(access_key, base_url)

if key_path:
    # Configure SSH parameters for all hosts
    final_hosts = []
    for hostname, attrs in hosts:
        host_params = {
            "ssh_key": key_path,
            "ssh_key_password": ssh_key_password,
            "ssh_port": attrs["ssh_port"],
            "ssh_paramiko_connect_kwargs": {}
        }

        # Add bastion configuration if present
        if attrs["bastion"]:
            # Create bastion transport
            bastion_client = SSHClient()
            bastion_client.set_missing_host_key_policy(AutoAddPolicy())
            
            try:
                bastion_client.connect(
                    attrs["bastion"]["hostname"],
                    port=attrs["bastion"]["port"],
                    username=attrs["bastion"]["ssh_user"],
                    key_filename=attrs["bastion"]["ssh_key"],
                    passphrase=attrs["bastion"]["ssh_key_password"],
                    look_for_keys=False
                )
                
                transport = bastion_client.get_transport()
                dest_addr = (hostname, attrs["ssh_port"])
                local_addr = ('127.0.0.1', 0)
                channel = transport.open_channel("direct-tcpip", dest_addr, local_addr)
                
                # Add channel to connection parameters
                host_params["ssh_paramiko_connect_kwargs"]["sock"] = channel
                
            except Exception as e:
                logger.error(f"Failed to connect to bastion for {hostname}: {str(e)}")
                continue

        final_hosts.append((
            hostname,
            {**attrs, **host_params}
        ))

    hosts = final_hosts

logger.info("\nSelected servers:")
for hostname, attrs in hosts:
    logger.info("- %s (User: %s)", hostname, attrs["ssh_user"])
    if attrs["bastion"]:
        logger.info("  ↳ Via bastion: %s:%d", 
                   attrs["bastion"]["hostname"], 
                   attrs["bastion"]["port"])