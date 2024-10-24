from pyinfra.operations import apt, apk, files, systemd, openrc
from pyinfra import host
from pyinfra.api import deploy

class UnsupportedOSError(Exception):
    pass

# Mapping for package managers and services based on OS
def setup_ubuntu():

    apt.packages(name="Install security tools", packages=["fail2ban", "ufw"], sudo=True)
    systemd.service(name="Enable Fail2Ban", service="fail2ban", running=True, enabled=True)
    systemd.service(name="Enable Firewall", service="ufw", running=True, enabled=True)

def setup_alpine():

    apk.packages(name="Install security tools", packages=["fail2ban", "iptables"], sudo=True)
    openrc.service(name="Enable Fail2Ban", service="fail2ban", running=True, enabled=True)
    openrc.service(name="Enable Firewall", service="iptables", running=True, enabled=True)

# OS setup mapping switch
OS_SETUP_FUNCTIONS = {
    'Ubuntu': setup_ubuntu,
    'Alpine': setup_alpine,
    # we can add more OS setup functions here
}


@deploy('Harden SSH and Security Setup')
def security_setup():
    # Fetch the OS name
    os_name = host.fact.linux_name

    try:
        # Execute the OS-specific setup function (like a switch-case)
        os_setup_function = OS_SETUP_FUNCTIONS.get(os_name)
        
        if os_setup_function is None:
            raise UnsupportedOSError(f"Security setup for {os_name} is not supported.")
        
        # Call the respective function to handle the setup
        os_setup_function()
    
    except UnsupportedOSError as e:
        print(e)

