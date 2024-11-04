from pyinfra.operations import apt, apk, systemd, openrc, server, files
from pyinfra import host, config
from pyinfra.api import deploy
from pyinfra.facts.server import LinuxName
from os.path import exists

config.SUDO = True
media = "/dev/sda1"  

class UnsupportedOSError(Exception):
    pass

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


# Sensitive paths for ACL
ACL_PATHS = {
    'Ubuntu': {
        '/etc/fail2ban': 'u:admin:rwx',  # Example ACL for a user
        '/var/log/lynis-report.dat': 'u:security:r',  # Restrict access to log file
        '/etc/audit/audit.rules': 'g:audit:rwx',  # Allow group access to audit rules
    },
    'Alpine': {
        '/etc/iptables/': 'u:admin:rx',  # Restrict iptables directory
        '/etc/suricata/': 'u:security:rw',  # Suricata config access for 'security' user
    },
}

# Mapping for package managers and services based on OS
def setup_ubuntu():
    apt.update(name="Update package lists")
    apt.upgrade(name="Upgrade all packages")

    # Install required security tools
    tools_to_install = [tool for tool, install in security_tools.items() if install]
    if tools_to_install:
        apt.packages(
            name="Install security tools",
            packages=tools_to_install
        )

    # Apply routing controls if required
    if security_tools["apparmor-utils"] or security_tools["auditd"]:
        systemd.service("apparmor", running=True, enabled=True)
        systemd.service("auditd", running=True, enabled=True)

    files.line(
        name="Enable positive source/destination address checks",
        path="/etc/sysctl.conf",
        line="net.ipv4.conf.all.rp_filter=1"
    )
    server.shell(name="Reload sysctl settings", commands=["sysctl -p"])

    # ClamAV configuration (only if installed)
    if security_tools["clamav"]:
        systemd.service("clamav-freshclam", running=False, enabled=True)
        server.shell(name="Update ClamAV database", commands="freshclam")
        systemd.service("clamav-freshclam", running=True, enabled=True)

    # Fail2Ban configuration (if installed)
    if security_tools["fail2ban"]:
        systemd.service("fail2ban", running=True, enabled=True)

    # Disable automatic security updates
    if not security_tools["unattended-upgrades"]:
        apt.packages(name="Remove unattended-upgrades", packages=["unattended-upgrades"], present=False)
    
    # Configure audit logs
    if security_tools["auditd"]:
        files.line(
            name="Enable logging for privileged operations",
            path="/etc/audit/auditd.conf",
            line="log_format = ENRICHED"
        )
        server.shell(name="Start audit logs for user activities", commands=["auditctl -e 1"])

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
        suricata_config_path = "/home/xoity/Desktop/infraninja/test/configs/ubuntu/suricata/suricata.yaml"
        if not exists(suricata_config_path):
            print(f"Suricata configuration file not found at {suricata_config_path}. Please ensure it exists.")
        else:
            files.put(
                name="Copy Suricata configuration file",
                src=suricata_config_path,
                dest="/etc/suricata/suricata.yaml"
            )

        systemd.service("suricata", running=True, enabled=True)
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

    set_acls("Ubuntu")


# Alpine setup with enhanced configurations
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

    set_acls("Alpine")


# OS setup mapping switch
OS_SETUP_FUNCTIONS = {
    'Ubuntu': setup_ubuntu,
    'Alpine': setup_alpine,
}

@deploy('Harden SSH and Security Setup')
def security_setup():
    # Fetch the OS name
    os = host.get_fact(LinuxName)
    try:
        # Execute the OS-specific setup function
        os_setup_function = OS_SETUP_FUNCTIONS.get(os)
        
        if os_setup_function is None:
            raise UnsupportedOSError(f"Security setup for {os} is not supported.")
        
        # Call the respective function to handle the setup
        os_setup_function()
    
    except UnsupportedOSError as e:
        print(e)


def set_acls(os_type):
    acls = ACL_PATHS.get(os_type, {})
    for path, acl_rule in acls.items():
        server.shell(
            name=f"Set ACL for {path}",
            commands=[f"setfacl -m {acl_rule} {path}"]
        )


