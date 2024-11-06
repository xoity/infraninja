from pyinfra.operations import apk, openrc, server, files
from pyinfra import host, config
from pyinfra.api import deploy
from os.path import exists

config.SUDO = True
media = "/dev/sda1"  


# ACL paths specific to Alpine
ACL_PATHS = {
    '/etc/iptables/': 'u:admin:rx',
    '/etc/suricata/': 'u:security:rw',
}


# Dictionary for tools and their installation status
security_tools = {
    "fail2ban": True,
    "apparmor-utils": True,
    "auditd": True,
    "clamav": False,  
    "clamav-daemon": False,  
    "lynis": True,
    "chkrootkit": True,
    "nmap": True,
    "suricata": False, 
    "unattended-upgrades": False,  
    "acl": True,
}

def setup_alpine():
    apk.update(name="Update package lists")
    apk.upgrade(name="Upgrade all packages")

    # Install required security tools
    tools_to_install = [tool for tool, install in security_tools.items() if install]
    
    if tools_to_install:
        apk.packages(
            name="Install security tools",
            packages=tools_to_install
        )

    # ClamAV configuration (only if installed)
    if security_tools["clamav"]:
        openrc.service("clamav-freshclam", running=False, enabled=True)
        server.shell(name="Update ClamAV database", commands="freshclam")
        openrc.service("clamav-freshclam", running=True, enabled=True)

    if security_tools["fail2ban"]:
        openrc.service("fail2ban", running=True, enabled=True)

    # Remove automatic updates
    if not security_tools.get("unattended-upgrades", True):
        apk.packages(name="Remove unattended-upgrades", packages=["unattended-upgrades"], present=False)
    
    # Disable removable media auto-run and ensure encryption
    files.line(
        name="Disable auto-run for removable media",
        path="/etc/apk/repositories",
        line="noauto"
    )
    server.shell(name="Ensure media encryption", commands=[f"cryptsetup luksFormat {media}"])

    # Lynis configuration and reporting
    if security_tools["lynis"]:
        server.shell(
            name="Run Lynis system audit",
            commands=["lynis audit system --report-file /var/log/lynis-report.dat"]
        )

    # Chkrootkit configuration and reporting
    if security_tools["chkrootkit"]:
        server.shell(
            name="Run chkrootkit scan and save report",
            commands=["chkrootkit > /var/log/chkrootkit.log"]
        )

    # Suricata IDS setup and logging
    if security_tools["suricata"]:
        suricata_config_path = "/home/xoity/Desktop/infraninja/test/configs/alpine/suricata/suricata.yaml"
        if not exists(suricata_config_path):
            print(f"Suricata configuration file not found at {suricata_config_path}. Please ensure it exists.")
        else:
            files.put(
                name="Copy Suricata configuration file",
                src=suricata_config_path,
                dest="/etc/suricata/suricata.yaml"
            )

        openrc.service("suricata", running=True, enabled=True)
        server.shell(
            name="Start Suricata with logging",
            commands=["suricata -c /etc/suricata/suricata.yaml -i eth0 -D > /var/log/suricata/suricata.log"]
        )

    # IPtables setup and logging
    server.shell(
        commands=[
            "iptables -P INPUT DROP",
            "iptables -P FORWARD DROP",
            "iptables -P OUTPUT ACCEPT",
            "iptables -A INPUT -p tcp --dport 22 -j ACCEPT",
            "iptables-save > /var/log/iptables-rules.log"
        ]
    )

    set_acls()


def set_acls():
    """
    Applies access control lists (ACLs) for specific security paths on Alpine.
    """
    for path, acl_rule in ACL_PATHS.items():
        server.shell(
            name=f"Set ACL for {path}",
            commands=[f"setfacl -m {acl_rule} {path}"]
        )
