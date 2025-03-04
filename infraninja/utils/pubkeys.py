import getpass
import json
import logging
import os
import threading
from typing import Any, Dict, List, Optional

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

    def _get_base_url(self) -> Optional[str]:
        """Get API base URL from environment."""
        if not self._base_url:
            self._base_url = os.getenv("JINN_API_URL")
            if not self._base_url:
                logger.error("Error: JINN_API_URL environment variable not set")
                return None
        return self._base_url

    def _get_credentials(self) -> Dict[str, str]:
        """Get user credentials either from cache or user input."""
        if self._credentials:
            logger.debug("Using cached credentials")
            return self._credentials

        username: str = input("Enter username: ")
        password: str = getpass.getpass("Enter password: ")
        self._credentials = {"username": username, "password": password}
        logger.debug("Credentials obtained from user input")
        return self._credentials

    def _make_auth_request(
        self, endpoint: str, method: str = "get", **kwargs: Any
    ) -> Optional[requests.Response]:
        """Make authenticated request to API."""
        if not self._session_key:
            return None

        headers = {
            "Authorization": f"Bearer {self._session_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        cookies = {"sessionid": self._session_key}

        try:
            response = requests.request(
                method, endpoint, headers=headers, cookies=cookies, timeout=30, **kwargs
            )
            return response if response.status_code == 200 else None
        except requests.exceptions.Timeout:
            logger.error("Request timed out")
        except requests.exceptions.RequestException as e:
            logger.error("Request failed: %s", str(e))
        return None

    def _login(self) -> bool:
        """Authenticate with the API and get a session key."""
        if self._session_key:
            return True

        base_url = self._get_base_url()
        if not base_url:
            return False

        credentials = self._get_credentials()
        login_endpoint = f"{base_url}/login/"
        headers = {"Content-Type": "application/json", "Accept": "application/json"}

        try:
            response = requests.post(
                login_endpoint,
                json=credentials,
                headers=headers,
                timeout=30,
            )

            if response.status_code != 200:
                logger.error(
                    "Login failed: %s - %s", response.status_code, response.text
                )
                return False

            response_data = response.json()
            self._session_key = response_data.get("session_key")
            return bool(self._session_key)

        except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
            logger.error("Login failed: %s", str(e))
            return False

    def fetch_ssh_keys(self, force_refresh: bool = False) -> Optional[List[str]]:
        """Fetch SSH keys from the API server."""
        if self._ssh_keys and not force_refresh:
            return self._ssh_keys

        if not self._login():
            return None

        base_url = self._get_base_url()
        if not base_url:
            return None

        response = self._make_auth_request(f"{base_url}/ssh-tools/ssh-keylist/")
        if not response:
            return None

        try:
            ssh_data = response.json()
            self._ssh_keys = [key_data["key"] for key_data in ssh_data["result"]]
            return self._ssh_keys
        except (KeyError, json.JSONDecodeError) as e:
            logger.error("Failed to parse SSH keys response: %s", str(e))
            return None

    @deploy("Add SSH keys to authorized_keys")
    def add_ssh_keys(self, force_refresh: bool = False) -> bool:
        """Add SSH keys to the authorized_keys file."""
        keys = self.fetch_ssh_keys(force_refresh)
        if not keys:
            logger.error("No SSH keys available to deploy")
            return False

        try:
            current_user = host.get_fact(User)
            user_details = host.get_fact(Users)[current_user]

            server.user_authorized_keys(
                name=f"Add SSH keys for {current_user}",
                user=current_user,
                group=user_details["group"],
                public_keys=keys,
                delete_keys=False,
            )
            return True

        except Exception as e:
            logger.error("Error setting up SSH keys: %s", str(e))
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
