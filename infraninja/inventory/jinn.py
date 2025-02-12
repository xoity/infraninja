# inventory || jinn.py

import os
import logging
import requests
from typing import Dict, Any, List, Tuple

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
)
logger = logging.getLogger(__name__)


INVENTORY_ENDPOINT = "/inventory/servers/"
SSH_CONFIG_DIR = os.path.expanduser("~/.ssh/config.d")
SSH_CONFIG_ENDPOINT = "/ssh-tools/ssh-config/?bastionless=true"
MAIN_SSH_CONFIG = os.path.expanduser("~/.ssh/config")


def get_groups_from_data(data):
    """Extract unique groups from server data."""
    groups = set()
    for server in data.get("result", []):
        group = server.get("group", {}).get("name_en")
        if group:
            groups.add(group)
    return sorted(list(groups))


def get_tags_from_data(servers: List[Dict]) -> List[str]:
    """Extract unique tags from server data."""
    tags = set()
    for server in servers:
        for tag in server.get("tags", []):
            if tag and not tag.isspace():  # Skip empty or whitespace-only tags
                tags.add(tag)
    return sorted(list(tags))


def fetch_ssh_config(base_url: str, api_key: str, bastionless: bool = True) -> str:
    """
    Fetch the SSH config from the API using an API key for authentication and return its content.
    """
    headers = {"Authentication": api_key}
    endpoint = f"{base_url.rstrip('/')}{SSH_CONFIG_ENDPOINT}"
    try:
        response = requests.get(
            endpoint, headers=headers, params={"bastionless": bastionless}, timeout=10
        )
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        raise RuntimeError("Failed to fetch SSH config: %s" % str(e))


def save_ssh_config(config_content: str, filename: str) -> None:
    """
    Save the SSH config content to a file in the SSH config directory.
    """
    os.makedirs(SSH_CONFIG_DIR, exist_ok=True)
    config_path = os.path.join(SSH_CONFIG_DIR, filename)
    with open(config_path, "w") as file:
        file.write(config_content)
    print("")
    logger.info("Saved SSH config to: %s", config_path)


def update_main_ssh_config():
    """
    Ensure the main .ssh/config includes the SSH config directory.
    """
    include_line = f"\nInclude {SSH_CONFIG_DIR}/*\n"
    if os.path.exists(MAIN_SSH_CONFIG):
        with open(MAIN_SSH_CONFIG, "r") as file:
            if include_line in file.read():
                return  # Already included

    with open(MAIN_SSH_CONFIG, "a") as file:
        file.write(include_line)
    logger.info("Updated main SSH config to include: %s/*", SSH_CONFIG_DIR)


def get_valid_filename(default_name: str = "bastionless_ssh_config") -> str:
    """Get a valid filename from user input."""
    while True:
        filename = input(
            f"Enter filename for SSH config [default: {default_name}]: "
        ).strip()
        if not filename:
            return default_name

        # Remove any directory components for security
        filename = os.path.basename(filename)

        # Check if filename is valid
        if not all(c.isalnum() or c in "-_." for c in filename):
            logger.warning(
                "Filename contains invalid characters. Use only letters, numbers, dots, hyphens, and underscores."
            )
            continue

        return filename


def fetch_servers(
    access_key: str, base_url: str, selected_group: str = None
) -> List[Tuple[str, Dict[str, Any]]]:
    try:
        # API call for servers
        headers = {"Authentication": access_key}
        response = requests.get(
            f"{base_url.rstrip('/')}{INVENTORY_ENDPOINT}", headers=headers
        )
        response.raise_for_status()
        data = response.json()

        # First, display available groups
        groups = get_groups_from_data(data)
        logger.info("\nAvailable groups:")
        for i, group in enumerate(groups, 1):
            logger.info("%d. %s", i, group)

        # If no group is selected, prompt for selection
        if selected_group is None:
            while True:
                choice = input(
                    "\nEnter group numbers (space-separated) or '*' for all groups: "
                ).strip()
                if choice in ("*", ""):
                    selected_groups = groups
                    break
                try:
                    # Split input and convert to integers
                    choices = [int(x) for x in choice.split()]
                    # Validate all choices
                    if all(1 <= x <= len(groups) for x in choices):
                        selected_groups = [groups[i - 1] for i in choices]
                        break
                    logger.warning("Invalid choice. Please select valid numbers.")
                except ValueError:
                    logger.warning("Please enter valid numbers or '*'.")

            logger.info("\nSelected groups: %s", ", ".join(selected_groups))

        else:
            selected_groups = [selected_group]

        # Filter servers by selected groups first
        filtered_servers = [
            server
            for server in data.get("result", [])
            if server.get("group", {}).get("name_en") in selected_groups
            and server.get("is_active", False)
        ]

        # Tag selection
        tags = get_tags_from_data(filtered_servers)
        if tags:
            logger.info("\nAvailable tags:")
            for i, tag in enumerate(tags, 1):
                logger.info(f"{i}. {tag}")

            tag_choice = input(
                "\nSelect tags (space-separated), '*' or Enter for all: "
            ).strip()

            if tag_choice and tag_choice != "*":
                try:
                    selected_indices = [int(i) - 1 for i in tag_choice.split()]
                    selected_tags = {
                        tags[i] for i in selected_indices if 0 <= i < len(tags)
                    }
                    # Filter servers by tags
                    filtered_servers = [
                        server
                        for server in filtered_servers
                        if any(tag in selected_tags for tag in server.get("tags", []))
                    ]
                except (ValueError, IndexError):
                    logger.warning("Invalid tag selection, showing all servers")

        # Convert to host list format
        hosts = [
            (
                server["ssh_hostname"],
                {
                    **server.get("attributes", {}),
                    "ssh_user": server.get("ssh_user"),
                    "is_active": server.get("is_active", False),
                    "group_name": server.get("group", {}).get("name_en"),
                    "tags": server.get("tags", []),
                    **{
                        key: value
                        for key, value in server.items()
                        if key
                        not in ["attributes", "ssh_user", "is_active", "group", "tags"]
                    },
                },
            )
            for server in filtered_servers
        ]

        return hosts

    except requests.exceptions.RequestException as e:
        logger.error("An error occurred while making the request: %s", e)
        return []
    except KeyError as e:
        logger.error("Error parsing response: %s", e)
        return []
    except Exception as e:
        logger.error("An unexpected error occurred: %s", e)
        return []


# use the os import to get the .ssh key path
key_path = os.path.expanduser("~/.ssh/id_rsa")

access_key = input("Please enter your access key: ")
base_url = input("Please enter the Jinn API base URL: ")
hosts = fetch_servers(access_key, base_url)


ssh_config = fetch_ssh_config(base_url, access_key, bastionless=True)

if ssh_config:
    filename = get_valid_filename()
    save_ssh_config(ssh_config, filename)
    update_main_ssh_config()  # Add this line to ensure the config is included
    logger.info("SSH configuration setup is complete.")

logger.info("\nSelected servers:")
for hostname, attrs in hosts:
    logger.info("- %s (User: %s)", hostname, attrs["ssh_user"])
