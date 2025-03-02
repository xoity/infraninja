import getpass
import json
import logging
import os
import threading
from typing import Any, Dict, List, Optional, TypeVar, cast

import requests
from pyinfra import host
from pyinfra.api import deploy
from pyinfra.facts.server import User, Users
from pyinfra.operations import server

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
)
logger = logging.getLogger(__name__)

# Define type variables for more precise typing
T = TypeVar("T")


class SSHKeyManager:
    """
    Manages SSH key operations including fetching from API and deploying to hosts.
    """

    # Class variables shared across all instances
    _ssh_keys: Optional[List[str]] = None
    _credentials: Optional[Dict[str, str]] = None
    _session_key: Optional[str] = None
    _base_url: Optional[str] = None
    _lock: threading.RLock = threading.RLock()  # Reentrant lock for thread safety
    _instance: Optional["SSHKeyManager"] = None  # Singleton instance

    @classmethod
    def get_instance(cls) -> "SSHKeyManager":
        """Get or create the singleton instance of SSHKeyManager."""
        if cls._instance is None:
            cls._instance = SSHKeyManager()
        return cls._instance

    def __init__(self) -> None:
        with self._lock:
            if SSHKeyManager._base_url is None:
                SSHKeyManager._base_url = os.getenv("JINN_API_URL")
                if not SSHKeyManager._base_url:
                    logger.error("Error: JINN_API_URL environment variable not set")

    def _get_credentials(self) -> Dict[str, str]:
        """Get user credentials either from cache or user input."""
        with self._lock:
            if SSHKeyManager._credentials is None:
                username: str = input("Enter username: ")
                password: str = getpass.getpass("Enter password: ")
                SSHKeyManager._credentials = {
                    "username": username,
                    "password": password,
                }
                logger.debug("Credentials obtained from user input")
            else:
                logger.debug("Using cached credentials")
            return cast(Dict[str, str], SSHKeyManager._credentials)

    def _login(self) -> bool:
        """
        Authenticate with the API and get a session key.

        Returns:
            bool: True if login successful, False otherwise.
        """
        with self._lock:
            if SSHKeyManager._session_key:
                logger.debug("Using existing session key")
                return True

            if not SSHKeyManager._base_url:
                return False

            credentials: Dict[str, str] = self._get_credentials()
            login_endpoint: str = f"{SSHKeyManager._base_url}/login/"
            login_data: Dict[str, str] = credentials
            headers: Dict[str, str] = {
                "Content-Type": "application/json",
                "Accept": "application/json",
            }

            try:
                logger.debug("Attempting login to API")
                response: requests.Response = requests.post(
                    login_endpoint, json=login_data, headers=headers, timeout=30
                )

                if response.status_code != 200:
                    logger.error(
                        "Login failed: %s - %s", response.status_code, response.text
                    )
                    return False

                response_data: Dict[str, Any] = response.json()
                SSHKeyManager._session_key = response_data.get("session_key")

                if not SSHKeyManager._session_key:
                    logger.error("Error: Session key missing in response.")
                    return False

                logger.debug("Login successful")
                return True

            except requests.exceptions.Timeout:
                logger.error("Connection timed out when contacting the API server")
            except requests.exceptions.ConnectionError:
                logger.error("Failed to connect to the API server")
            except json.JSONDecodeError:
                logger.error("Invalid JSON response received from the API server")
            except Exception as e:
                logger.error(
                    "Unexpected error during login: %s: %s", type(e).__name__, e
                )
            return False

    def fetch_ssh_keys(self, force_refresh: bool = False) -> Optional[List[str]]:
        """
        Fetch SSH keys from the API server.

        Args:
            force_refresh: If True, bypass cache and fetch new keys.

        Returns:
            Optional[List[str]]: List of SSH public keys if successful, None otherwise.
        """
        with self._lock:
            if SSHKeyManager._ssh_keys is not None and not force_refresh:
                logger.debug("Using cached SSH keys")
                return SSHKeyManager._ssh_keys

            if not SSHKeyManager._session_key and not self._login():
                return None

            auth_headers: Dict[str, str] = {
                "Authorization": f"Bearer {SSHKeyManager._session_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            }

            cookies: Dict[str, str] = {
                "sessionid": cast(str, SSHKeyManager._session_key)
            }
            ssh_endpoint: str = f"{SSHKeyManager._base_url}/ssh-tools/ssh-keylist/"

            try:
                logger.debug("Fetching SSH keys from API")
                ssh_response: requests.Response = requests.get(
                    ssh_endpoint, headers=auth_headers, cookies=cookies, timeout=30
                )

                if ssh_response.status_code != 200:
                    logger.error("Failed to retrieve SSH keys: %s", ssh_response.text)
                    return None

                ssh_data: Dict[str, Any] = ssh_response.json()
                SSHKeyManager._ssh_keys = [
                    key_data["key"] for key_data in ssh_data["result"]
                ]
                logger.debug(
                    "Successfully retrieved %s SSH keys", len(SSHKeyManager._ssh_keys)
                )
                return SSHKeyManager._ssh_keys

            except Exception as e:
                logger.error("Error fetching SSH keys: %s: %s", type(e).__name__, e)
                return None

    @deploy("Add SSH keys to authorized_keys")
    def add_ssh_keys(self, force_refresh: bool = False) -> bool:
        """
        Add SSH keys to the authorized_keys file of the current user.

        Args:
            force_refresh: If True, bypass cache and fetch new keys.

        Returns:
            bool: True if keys were added successfully, False otherwise.
        """
        keys: Optional[List[str]] = self.fetch_ssh_keys(force_refresh)

        if not keys:
            logger.error("No SSH keys available to deploy")
            return False

        try:
            # Get current user details
            current_user: str = host.get_fact(User)
            user_details: Dict[str, Any] = host.get_fact(Users)[current_user]

            # Add keys using server operation
            server.user_authorized_keys(
                name=f"Add SSH keys for {current_user}",
                user=current_user,
                group=user_details["group"],
                public_keys=keys,
                delete_keys=False,
            )

            return True

        except (KeyError, AttributeError) as e:
            logger.error("Error getting user details: %s", e)
        except Exception as e:
            logger.error("Error setting up SSH keys: %s", e)

        return False

    def clear_cache(self) -> bool:
        """
        Clear all cached credentials and keys.

        Returns:
            bool: True if cache was cleared successfully.
        """
        with self._lock:
            SSHKeyManager._credentials = None
            SSHKeyManager._ssh_keys = None
            SSHKeyManager._session_key = None
            logger.debug("Cache cleared")
            return True


# For backward compatibility with existing code - use the singleton pattern
def add_ssh_keys() -> bool:
    """
    Backward compatibility function that uses the singleton instance.

    Returns:
        bool: True if keys were added successfully, False otherwise.
    """
    manager: SSHKeyManager = SSHKeyManager.get_instance()
    return manager.add_ssh_keys()
