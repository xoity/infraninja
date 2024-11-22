import os
import requests

# defined the hosts variable as a list of tuples
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
            (
                server["ssh_hostname"],
                {
                    **server.get("attributes", {}),
                    "ssh_user": server.get("ssh_user"),
                    "is_active": server.get("is_active", False),
                    "install_postgres": server.get("attributes", {}).get("docker", "False") == "True",
                    "group_name": server.get("group", {}).get("name_en"),
                },
            )
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
hosts = fetch_servers(access_key)
