import os
import requests
import getpass
from pyinfra.operations import server
from pyinfra.api import deploy
from pyinfra import host
from pyinfra.facts.server import User, Users
import logging
import json

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
)
logger = logging.getLogger(__name__)

# Module-level variables to store credentials and SSH keys
_cached_ssh_keys = None
_cached_credentials = None


@deploy("Add SSH keys to authorized_keys")
def add_ssh_keys():
    global _cached_ssh_keys, _cached_credentials

    # Get base_url from environment variable
    base_url = os.getenv("JINN_API_URL")
    if not base_url:
        logger.error("Error: JINN_API_URL environment variable not set")
        return False

    # If SSH keys are already cached, use them
    if _cached_ssh_keys is None:
        # Only ask for credentials if we don't have them
        if _cached_credentials is None:
            username = input("Enter username: ")
            password = getpass.getpass("Enter password: ")
            _cached_credentials = {"username": username, "password": password}
        else:
            username = _cached_credentials["username"]
            password = _cached_credentials["password"]

        login_endpoint = f"{base_url}/login/"
        login_data = {"username": username, "password": password}

        headers = {"Content-Type": "application/json", "Accept": "application/json"}

        try:
            response = requests.post(
                login_endpoint, json=login_data, headers=headers, timeout=30
            )  # Add timeout

            if response.status_code != 200:
                logger.error(
                    "Login failed: %s - %s", response.status_code, response.text
                )
                return False

            response_data = response.json()
            session_key = response_data.get("session_key")

            if not session_key:
                logger.error("Error: Session key missing in response.")
                return

            auth_headers = {
                "Authorization": f"Bearer {session_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            }

            cookies = {"sessionid": session_key}

            ssh_endpoint = f"{base_url}/ssh-tools/ssh-keylist/"
            ssh_response = requests.get(
                ssh_endpoint, headers=auth_headers, cookies=cookies
            )

            if ssh_response.status_code != 200:
                logger.error("Failed to retrieve SSH keys: %s", ssh_response.text)
                return

            ssh_data = ssh_response.json()

            # Store the SSH keys for future use
            _cached_ssh_keys = [key_data["key"] for key_data in ssh_data["result"]]

        except requests.exceptions.Timeout:
            logger.error("Connection timed out when contacting the API server")
            return False
        except requests.exceptions.ConnectionError:
            logger.error("Failed to connect to the API server")
            return False
        except json.JSONDecodeError:
            logger.error("Invalid JSON response received from the API server")
            return False
        except Exception as e:
            logger.error(
                "Unexpected error during SSH key setup: %s: %s", type(e).__name__, e
            )
            return False

    try:
        # Get current user details using proper fact classes
        current_user = host.get_fact(User)
        user_details = host.get_fact(Users)[current_user]

        # Add keys using server operation
        server.user_authorized_keys(
            name=f"Add SSH keys for {current_user}",
            user=current_user,
            group=user_details["group"],
            public_keys=_cached_ssh_keys,
            delete_keys=False,
        )

    except (KeyError, AttributeError) as e:
        logger.error("Error getting user details: %s", e)
        return False
    except Exception as e:
        logger.error("Error setting up SSH keys: %s", e)
        return False

    return True
