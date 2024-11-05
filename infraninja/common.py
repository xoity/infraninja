from pyinfra.operations import apt, apk, files, server, systemd, openrc
from pyinfra import host, config
from pyinfra.api import deploy
from pyinfra.facts.server import LinuxName

os = host.get_fact(LinuxName)  
config.SUDO = True

# we can add common services that are not needed in most cases, scalable.
common_services = ["avahi-daemon", "cups", "bluetooth", "rpcbind", "vsftpd", "telnet"] # network discovery, printing, bluetooth, rpc for NTFs, ftp, telnet

ssh_config = {
        "PermitRootLogin": "prohibit-password",
        "PasswordAuthentication": "no",
        "X11Forwarding": "no",
    }


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

    for option, value in ssh_config.items():
        files.replace(
            name=f"Configure SSH: {option}",
            path="/etc/ssh/sshd_config",
            # select the entire line starting with the option from the file in path and delete the old option (e.g. PermitRootLogin) and replace it with the new value (e.g. prohibit-password) and remove the old value (e.g. yes), and if the line has a comment in the start, remove that comment and replace it with the new value
            line=f"^{option} .*$",
            replace=f"{option} {value}",  # Ensure only the intended setting remains
        )

@deploy('UAE IA compliance')
def uae_ia_compliance():
    
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

@deploy('Disable useless services common')
def disable_useless_services_common():
    for service in common_services:
        if os == 'Ubuntu':
            systemd.service(service, running=False, enabled=False)
        if os == 'Alpine':
            openrc.service(service, running=False, enabled=False)
    
