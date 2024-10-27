from pyinfra.operations import apt, apk, files, server
from pyinfra import host, config
from pyinfra.api import deploy
from pyinfra.facts.server import LinuxName

os = host.get_fact(LinuxName)  
config.SUDO = True
@deploy('Common System Updates')
def system_update():
    if os == 'Ubuntu':
        apt.update(name="Update Ubuntu package lists")
        apt.upgrade(name="Upgrade Ubuntu packages")
    elif os == 'Alpine':
        apk.update(name="Update Alpine package lists")
        apk.upgrade(name="Upgrade Alpine packages")
    else:
        raise ValueError(f"Unsupported OS: {os}")

@deploy("ssh common hardening test")
def ssh_common_hardening():

    ssh_config = {
        "PermitRootLogin": "prohibit-password",
        "PasswordAuthentication": "no",
        "X11Forwarding": "no",
    }

    # Apply SSH configuration
    for option, value in ssh_config.items():
        files.line(
            name=f"Configure SSH: {option}",
            path="/etc/ssh/sshd_config",
            line=f"{option} {value}"
        )


@deploy('UAE IA compliance')
def uae_ia_compliance():
        
    # T3.6.2: Capture user activities, exceptions, security events, and more
    files.line(
        name="Log user activity and system events",
        path="/etc/audit/audit.rules",
        line="-w /etc/passwd -p wa -k identity\n-w /etc/shadow -p wa -k auth\n-w /var/log/auth.log -p wa -k logins"
    )

    # T3.6.3: Log privileged operations and unauthorized access attempts
    files.line(
        name="Log privileged operations and unauthorized access",
        path="/etc/audit/audit.rules",
        line="-w /sbin/ifconfig -p x -k network"
    )

    # T4.5.1 - T4.5.4: Network components inventory and scanning
    server.shell(
        name="Network scanning and port checks",
        commands=["nmap -sS localhost"]
    )

    # Regular scan and capture version changes in services
    server.shell(
        name="Port scan for changes in services",
        commands=["nmap -O localhost > /var/log/nmap.log"]
    )

    # Backup firewall configurations regularly
    server.shell(
        name="Backup firewall configuration",
        commands=["iptables-save > /etc/firewall.backup"]
    )
