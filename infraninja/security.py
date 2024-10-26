from pyinfra.operations import apt, apk, systemd, openrc
from pyinfra import host, config
from pyinfra.api import deploy
from pyinfra.facts.server import LinuxName


config.SUDO = True

class UnsupportedOSError(Exception):
    pass

# Mapping for package managers and services based on OS
def setup_ubuntu():

    apt.packages(name="Install security tools", packages=["fail2ban", "ufw"])
    systemd.service(name="Enable Fail2Ban", service="fail2ban", running=True, enabled=True)
    systemd.service(name="Enable Firewall", service="ufw", running=True, enabled=True)

def setup_alpine():

    apk.packages(name="Install security tools", packages=["fail2ban", "iptables"])
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
    os = host.get_fact(LinuxName)
    try:
        # Execute the OS-specific setup function (like a switch-case)
        os_setup_function = OS_SETUP_FUNCTIONS.get(os)
        
        if os_setup_function is None:
            raise UnsupportedOSError(f"Security setup for {os} is not supported.")
        
        # Call the respective function to handle the setup
        os_setup_function()
    
    except UnsupportedOSError as e:
        print(e)

