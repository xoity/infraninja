from pyinfra.operations import apt, files, server, systemd
from pyinfra import config
from os.path import exists


config.SUDO = True
media = "/dev/sda1"  

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
    "acl": True,
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
    
    # Fail2Ban configuration (configure it)
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
        files.line(
        name="Log user activity and system events",
        path="/etc/audit/audit.rules",
        line="-w /etc/passwd -p wa -k identity\n-w /etc/shadow -p wa -k auth\n-w /var/log/auth.log -p wa -k logins"
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
      
    server.shell(name="Ensure media encryption", commands=[f"cryptsetup luksFormat {media}"])

    set_acls()


def set_acls():
    
    ACL_PATHS = {
        '/etc/fail2ban': 'u:admin:rwx',
        '/var/log/lynis-report.dat': 'u:security:r',
        '/etc/audit/audit.rules': 'g:audit:rwx',
    }

    for path, acl_rule in ACL_PATHS.items():
        server.shell(
            name=f"Set ACL for {path}",
            commands=[f"setfacl -m {acl_rule} {path}"]
        )
