from pyinfra import config
from pyinfra.api import deploy
from pyinfra.operations import files, server, systemd

config.SUDO = True

@deploy("iptables Setup for Ubuntu")
def iptables_setup():
    # Define iptables rules as a string
    iptables_rules = """
# Flush existing rules
iptables -F

# Set default policies
iptables -P INPUT DROP
iptables -P FORWARD DROP
iptables -P OUTPUT ACCEPT

# Allow loopback traffic
iptables -A INPUT -i lo -j ACCEPT

# Allow established and related incoming traffic
iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT

# Allow incoming SSH
iptables -A INPUT -p tcp --dport 22 -j ACCEPT

# Logging rules for incoming traffic
iptables -A INPUT -j LOG --log-prefix "iptables-input: " --log-level 4

# Save the rules to make them persistent
iptables-save > /etc/iptables/rules.v4
    """

    # Path for temporary local iptables rules file
    iptables_rules_path = "/tmp/setup_iptables.sh"
    with open(iptables_rules_path, "w") as f:
        f.write(iptables_rules)

    # Upload and apply iptables configuration script
    files.put(
        name="Upload iptables rules script",
        src=iptables_rules_path,
        dest="/usr/local/bin/setup_iptables.sh",
        mode="755",  # Make the script executable
    )

    # Ensure the /etc/iptables directory exists
    server.shell(
        name="Create /etc/iptables directory",
        commands="mkdir -p /etc/iptables",
    )

    # Run the iptables configuration script to apply the rules
    server.shell(
        name="Run iptables setup script",
        commands="/usr/local/bin/setup_iptables.sh",
    )

    # Enable iptables-persistent to restore rules on reboot
    systemd.service(
        name="Enable iptables-persistent to restore rules on reboot",
        service="netfilter-persistent",
        running=True,
        enabled=True,
    )

    # Create a log directory for iptables
    server.shell(
        name="Create iptables log directory",
        commands="mkdir -p /var/log/iptables",
    )

    # Log rotation configuration content for iptables
    logrotate_config = """
/var/log/iptables/iptables.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    create 0640 root adm
    sharedscripts
    postrotate
        /etc/init.d/rsyslog reload > /dev/null
    endscript
}
    """

    # Path for temporary local logrotate configuration file
    logrotate_config_path = "/tmp/logrotate_iptables"
    with open(logrotate_config_path, "w") as f:
        f.write(logrotate_config)

    # Upload logrotate configuration file
    files.put(
        name="Upload iptables logrotate configuration",
        src=logrotate_config_path,
        dest="/etc/logrotate.d/iptables",
        mode="644",
    )