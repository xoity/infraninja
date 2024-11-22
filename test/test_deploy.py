import pyinfra
from pyinfra.api import deploy
from infraninja.security.common.update_packages import system_update
from infraninja.security.common.acl import acl_setup
from inventory import fetch_servers

@deploy('Test Security Setup')
def test_deploy():
    system_update()
    acl_setup()  # Add this line to apply ACL rules

def main():
    access_key = input("Enter your access key: ")
    hosts = fetch_servers(access_key)
    if not hosts:
        print("No valid hosts found.")
        return

    # Execute the deploy on the fetched VMs
    pyinfra.api.deploy(
        test_deploy(),
        hosts=hosts
    )

if __name__ == "__main__":
    main()



