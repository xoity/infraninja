from pyinfra.api import deploy
from pyinfra.operations import files, server

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
    
