from pyinfra.operations import apt, apk, systemd, openrc, server, files
from pyinfra import host, config
from pyinfra.api import deploy
from pyinfra.facts.server import LinuxName


config.SUDO = True

class UnsupportedOSError(Exception):
    pass

# Mapping for package managers and services based on OS
def setup_ubuntu():
    # Update and upgrade packages
    apt.update(name="Update package lists")
    apt.upgrade(name="Upgrade all packages")

    # Install required security tools
    apt.packages(name="Install security tools", packages=["fail2ban", "apparmor-utils", "auditd", "clamav", "clamav-daemon", "lynis", "chkrootkit", "nmap"])

    # T5.4.6: Apply routing controls (Source & Destination Address Checks)
    systemd.service("apparmor", running=True, enabled=True)
    systemd.service("auditd", running=True, enabled=True)

    files.line(
        name="Enable positive source/destination address checks",
        path="/etc/sysctl.conf",
        line="net.ipv4.conf.all.rp_filter=1"
    )
    server.shell(name="Reload sysctl settings", commands=["sysctl -p"])

    # T3.4.1: Anti-malware configurations and update ClamAV
    systemd.service("clamav-freshclam", running=False, enabled=True)
    server.shell(name="Update ClamAV database", commands="freshclam")
    systemd.service("clamav-freshclam", running=True, enabled=True)
    
    # Configure Fail2Ban for malware detection and logging
    systemd.service("fail2ban", running=True, enabled=True)

    # Disable automatic security updates
    apt.packages(name="Remove unattended-upgrades", packages=["unattended-upgrades"], present=False)
    
    files.line(
        name="Disable automatic updates ",
        path="/etc/apt/apt.conf.d/10periodic",
        line="APT::Periodic::Enable \"0\";",
    )
    
    # T3.6: Audit and Logging - Access logs and privileged operations
    files.line(
        name="Enable logging for privileged operations",
        path="/etc/audit/auditd.conf",
        line="log_format = ENRICHED"
    )

    server.shell(
        name="Start audit logs for user activities",
        commands=["auditctl -e 1"]
    )
    
def setup_alpine():

    apk.update(name="Update package lists")
    apk.upgrade(name="Upgrade all packages")

    # Install required security tools
    apk.packages(name="Install security tools", packages=["fail2ban", "clamav", "clamav-daemon", "lynis", "chkrootkit"])

    # Configure services and disable automatic updates
    openrc.service("clamav-freshclam", running=False, enabled=True)
    server.shell(name="Update ClamAV database", commands="freshclam")
    openrc.service("clamav-freshclam", running=True, enabled=True)
    openrc.service("fail2ban", running=True, enabled=True)

    apk.packages(name="Remove unattended-upgrades", packages=["unattended-upgrades"], present=False)
    
    # T1.4.1: Disable removable media auto-run and enforce encryption
    files.line(
        name="Disable auto-run for removable media",
        path="/etc/apk/repositories",
        line="noauto"
    )

    media = "/dev/sda1"  # replace with actual media device
    server.shell(
        name="Ensure media encryption",
        commands=[f"cryptsetup luksFormat {media}"] 
    )

    # T1.2.1: Manage firewall/IDS/IPS devices
    server.shell(
        name="Ensure firewall and IDS/IPS are installed and configured",
        commands=["apk add iptables", "apk add suricata"]  # IDS/IPS template 
    )
    openrc.service("iptables", running=True, enabled=True)
    openrc.service("suricata", running=True, enabled=True)  # IDS/IPS template



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

