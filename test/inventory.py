import requests


def get_groups_from_data(data):
    """Extract unique groups from server data."""
    groups = set()
    for server in data.get("result", []):
        group = server.get("group", {}).get("name_en")
        if group:
            groups.add(group)
    return sorted(list(groups))


def fetch_servers(access_key, selected_group=None):
    headers = {"Authentication": access_key}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()

        # First, display available groups
        groups = get_groups_from_data(data)
        print("\nAvailable groups:")
        for i, group in enumerate(groups, 1):
            print(f"{i}. {group}")

        # If no group is selected, prompt for selection
        if selected_group is None:
            while True:
                try:
                    choice = int(input("\nSelect a group number: "))
                    if 1 <= choice <= len(groups):
                        selected_group = groups[choice - 1]
                        break
                    print("Invalid choice. Please select a valid number.")
                except ValueError:
                    print("Please enter a valid number.")

        print(f"\nSelected group: {selected_group}")

        # Filter servers by selected group
        return [
            (
                server["ssh_hostname"],
                {
                    **server.get("attributes", {}),
                    "ssh_user": server.get("ssh_user"),
                    "is_active": server.get("is_active", False),
                    "install_postgres": server.get("attributes", {}).get(
                        "docker", "False"
                    )
                    == "True",
                    "group_name": server.get("group", {}).get("name_en"),
                },
            )
            for server in data.get("result", [])
            if server.get("group", {}).get("name_en") == selected_group
            and server.get("is_active", False)  # Only include active servers
        ]

    except requests.exceptions.RequestException as e:
        print("An error occurred while making the request:", e)
        return []
    except KeyError as e:
        print("Error parsing response:", e)
        return []
    except Exception as e:
        print("An unexpected error occurred:", e)
        return []


# Example usage
access_key = input("Enter your access key: ")
url = input("Enter the URL to fetch servers: ")
hosts = fetch_servers(access_key)

# Print selected servers for confirmation
print("\nSelected servers:")
for hostname, attrs in hosts:
    print(f"- {hostname} (User: {attrs['ssh_user']})")
