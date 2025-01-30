import requests
import json
import getpass
from pyinfra.operations import files
from pyinfra import host
import logging
from pyinfra.api import deploy


logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

@deploy("Fetch and append SSH keys")
def main():

    username = input("Enter your Jinn Username: ")
    password = getpass.getpass("Enter your Jinn Password: ")
    base_url = input("Enter the base URL of the Jinn API:")



    try:
        url_login = f"{base_url.rstrip('/')}/login"
        login_data = {
            "username": username,
            "password": password
        }
        response = requests.post(
            url_login, 
            json=login_data,  
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        response.raise_for_status()
            
        session_data = response.json()
        session_key = session_data.get('session_key')
    except requests.RequestException as e:
        raise RuntimeError(f"Login failed: {str(e)}")
    except json.JSONDecodeError:
        raise RuntimeError("Invalid JSON response from login endpoint")

    """Fetch public keys using session key"""
    try:
        url_pubkeys = f"{base_url.rstrip('/')}/ssh-tools/ssh-keylist"
        headers = {"Authorization": f"Bearer {session_key}"}
        cookies = {"session_key": session_key}
        response = requests.get(url_pubkeys, cookies=cookies, headers=headers, timeout=10)
        response.raise_for_status()
            
        data = response.json()
        pubkey = data.get('result', [])
    except requests.RequestException as e:
        raise RuntimeError(f"Failed to fetch public keys: {str(e)}")
    except json.JSONDecodeError:
        raise RuntimeError("Invalid JSON response from pubkeys endpoint")

    """Append SSH keys to authorized_keys file using pyinfra"""
    try:
        auth_keys_file = "~/.ssh/authorized_keys"
            
        # Ensure .ssh directory exists with correct permissions
        files.directory(
            name="Ensure .ssh directory exists",
            path="~/.ssh",
            mode=700,
            user=host.get_fact('user'),
            group=host.get_fact('group')
        )

        # Extract and format keys
        key_strings = []
        for key_data in pubkey:
            if key_data.get('key'):
                key_strings.append(f"{key_data['key']} # {key_data.get('label', 'No label')}")

        if not key_strings:
            logger.warning("No valid keys found to append")
                

            # Append keys to authorized_keys file
            files.line(
                name="Append SSH keys to authorized_keys",
                path=auth_keys_file,
                mode=600,
                lines=key_strings,
                present=True
            )

            logger.info(f"Successfully appended {len(key_strings)} keys to {auth_keys_file}")

    except Exception as e:
        raise RuntimeError(f"Failed to append keys: {str(e)}")




