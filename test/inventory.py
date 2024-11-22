import os
import requests

# Define the hosts variable as a list of tuples
def fetch_servers(access_key):
    url = "https://jinn-beta.kalvad.cloud/inventory/getServers/"
    headers = {
        "Authentication": access_key
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        return [
            (server["ip"], {"ssh_user": server["ssh_user"], "ssh_key": server["ssh_key"]})
            for server in data.get("result", [])
        ]
    except requests.exceptions.RequestException as e:
        print("An error occurred while making the request:", e)
        print("No hosts will be fetched.")
        return []
    except KeyError as e:
        print("Error parsing response:", e)
        print("No hosts will be fetched.")
        return []
    except Exception as e:
        print("An unexpected error occurred:", e)
        print("No hosts will be fetched.")
        return []

# Example usage
access_key = os.getenv("ACCESS_KEY")  # Read the access key from environment variable
if not access_key:
    print("ACCESS_KEY environment variable is not set.")
else:
    hosts = fetch_servers(access_key)