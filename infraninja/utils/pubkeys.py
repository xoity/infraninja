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


def attempt_login(base_url, max_retries=3):
    """Helper function to handle login with retry capability"""
    for attempt in range(max_retries):
        if attempt > 0:
            logger.info("\nRetry attempt %d of %d", attempt, max_retries - 1)

        username = input("Enter username: ")
        password = getpass.getpass("Enter password: ")

        login_endpoint = f"{base_url}/login/"
        login_data = {"username": username, "password": password}
        headers = {"Content-Type": "application/json", "Accept": "application/json"}

        try:
            response = requests.post(
                login_endpoint, json=login_data, headers=headers, timeout=30
            )

            if response.status_code == 401:
                # Extract a more user-friendly error message
                try:
                    error_data = response.json()
                    error_message = error_data.get("message", "Authentication failed")
                    logger.error("Login failed: %s", error_message)
                except Exception:
                    logger.error("Login failed: Invalid credentials")

                if attempt < max_retries - 1:
                    continue
                return None, None

            if response.status_code != 200:
                logger.error(
                    "Login failed: %s - %s", response.status_code, response.text
                )
                if attempt < max_retries - 1:
                    continue
                return None, None

            response_data = response.json()
            session_key = response_data.get("session_key")

            if not session_key:
                logger.error("Error: Session key missing in response.")
                if attempt < max_retries - 1:
                    continue
                return None, None

            return username, session_key

        except requests.exceptions.Timeout:
            logger.error("Connection timed out when contacting the API server")
        except requests.exceptions.ConnectionError:
            logger.error("Failed to connect to the API server")
        except json.JSONDecodeError:
            logger.error("Invalid JSON response received from the API server")
        except Exception as e:
            logger.error("Unexpected error during login: %s: %s", type(e).__name__, e)

        if attempt < max_retries - 1:
            continue
        return None, None


@deploy("Add SSH keys to authorized_keys")
def add_ssh_keys():
    # Get base_url from environment variable
    base_url = os.getenv("JINN_API_URL")
    if not base_url:
        logger.error("Error: JINN_API_URL environment variable not set")
        return False

    username, session_key = attempt_login(base_url)
    if not session_key:
        logger.error("Authentication failed after multiple attempts. Aborting.")
        return False

    auth_headers = {
        "Authorization": f"Bearer {session_key}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    cookies = {"sessionid": session_key}

    try:
        ssh_endpoint = f"{base_url}/ssh-tools/ssh-keylist/"
        ssh_response = requests.get(ssh_endpoint, headers=auth_headers, cookies=cookies)

        if ssh_response.status_code != 200:
            logger.error("Failed to retrieve SSH keys: %s", ssh_response.text)
            return False

        ssh_data = ssh_response.json()

        try:
            # Get current user details using proper fact classes
            current_user = host.get_fact(User)
            user_details = host.get_fact(Users)[current_user]

            # Extract public keys from response
            public_keys = [key_data["key"] for key_data in ssh_data["result"]]

            # Add keys using server operation
            server.user_authorized_keys(
                name=f"Add SSH keys for {current_user}",
                user=current_user,
                group=user_details["group"],
                public_keys=public_keys,
                delete_keys=False,
            )

        except (KeyError, AttributeError) as e:
            logger.error("Error getting user details: %s", e)
            return False
        except Exception as e:
            logger.error("Error setting up SSH keys: %s", e)
            return False

        return True

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
