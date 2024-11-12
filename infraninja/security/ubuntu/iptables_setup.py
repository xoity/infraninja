from pyinfra.operations import files, server, systemd
from pyinfra.api import deploy
from pyinfra import config

config.SUDO = True

@deploy("iptables Setup")
def iptabels_setup():

    # Define a basic set of iptables rules for security 
    iptables_rules = """
    # Flush existing rules
    iptables -F

    # Default policy to drop all traffic
    iptables -P INPUT DROP
    iptables -P FORWARD DROP
    iptables -P OUTPUT ACCEPT

    # Allow loopback interface
    iptables -A INPUT -i lo -j ACCEPT
    iptables -A OUTPUT -o lo -j ACCEPT

    # Allow incoming SSH (adjust port if needed)
    iptables -A INPUT -p tcp --dport 22 -j ACCEPT

    # Allow incoming HTTP and HTTPS traffic
    iptables -A INPUT -p tcp --dport 80 -j ACCEPT
    iptables -A INPUT -p tcp --dport 443 -j ACCEPT

    # Allow established connections
    iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT

    # Logging rules for incoming traffic
    iptables -A INPUT -j LOG --log-prefix "iptables-input: " --log-level 4

    # Save the rules to make them persistent
    iptables-save > /etc/iptables/rules.v4
    """

    # Upload and apply iptables configuration script
    files.put(
        name="Upload iptables rules script",
        src=iptables_rules,
        dest="/usr/local/bin/setup_iptables.sh",
        mode="755",  # Make the script executable
    )

    # Step 3: Run the iptables configuration script to apply the rules
    server.shell(
        name="Run iptables setup script",
        commands="/usr/local/bin/setup_iptables.sh",
    )

    # Step 4: Set up iptables to persist rules after reboot
    systemd.service(
        name="Enable iptables-persistent to restore rules on reboot",
        service="netfilter-persistent",
        running=True,
        enabled=True,
    )

    # Step 5: Ensure log directory for iptables exists
    server.shell(
        name="Create iptables log directory",
        commands="mkdir -p /var/log/iptables",
    )

    # Step 6: Configure log rotation for iptables logs

    logrotate_config = """
    /var/log/iptables/iptables.log {
        daily
        rotate 7
        compress
        delaycompress
        missingok
        notifempty
        postrotate
            /etc/init.d/iptables reload > /dev/null 2>&1 || true
        endscript
    }
    """

    # Apply log rotation settings for iptables logs
    files.put(
        name="Upload iptables logrotate configuration",
        src=logrotate_config,
        dest="/etc/logrotate.d/iptables",
    )
