from pyinfra.api import deploy
from pyinfra.operations import iptables, server, openrc, files

@deploy("iptables Setup for Alpine Linux")
def iptables_setup_alpine():
    # Ensure chains exist before flushing
    iptables.chain(
        name="Ensure INPUT chain exists",
        chain="INPUT",
        present=True,
    )
    iptables.chain(
        name="Ensure FORWARD chain exists",
        chain="FORWARD",
        present=True,
    )
    iptables.chain(
        name="Ensure OUTPUT chain exists",
        chain="OUTPUT",
        present=True,
    )

    # Flush existing rules within chains
    iptables.rule(
        name="Flush existing rules in INPUT chain",
        chain="INPUT",
        jump="ACCEPT",
        present=False,
    )
    iptables.rule(
        name="Flush existing rules in FORWARD chain",
        chain="FORWARD",
        jump="ACCEPT",
        present=False,
    )
    iptables.rule(
        name="Flush existing rules in OUTPUT chain",
        chain="OUTPUT",
        jump="ACCEPT",
        present=False,
    )

    # Set default policies
    iptables.chain(
        name="Set default policy for INPUT",
        chain="INPUT",
        policy="DROP",
    )
    iptables.chain(
        name="Set default policy for FORWARD",
        chain="FORWARD",
        policy="DROP",
    )
    iptables.chain(
        name="Set default policy for OUTPUT",
        chain="OUTPUT",
        policy="ACCEPT",
    )

    # Allow loopback traffic
    iptables.rule(
        name="Allow loopback traffic",
        chain="INPUT",
        jump="ACCEPT",
        in_interface="lo",
    )

    # Allow established and related incoming traffic
    iptables.rule(
        name="Allow established and related incoming traffic",
        chain="INPUT",
        jump="ACCEPT",
        extras="-m state --state ESTABLISHED,RELATED",
    )

    # Allow incoming SSH
    iptables.rule(
        name="Allow incoming SSH",
        chain="INPUT",
        jump="ACCEPT",
        protocol="tcp",
        destination_port=22,
    )

    # Logging rules for incoming traffic
    iptables.rule(
        name="Log incoming traffic",
        chain="INPUT",
        jump="LOG",
        log_prefix="iptables-input: ",
    )

    # Save the rules to make them persistent
    server.shell(
        name="Save iptables rules",
        commands="iptables-save > /etc/iptables/rules.v4",
    )

    # Ensure the /etc/iptables directory exists
    server.shell(
        name="Create /etc/iptables directory",
        commands="mkdir -p /etc/iptables",
    )

    # Enable iptables-persistent to restore rules on reboot
    openrc.service(
        name="Enable iptables-persistent to restore rules on reboot",
        service="iptables",
        running=True,
        enabled=True,
    )

    # Create a log directory for iptables
    server.shell(
        name="Create iptables log directory for Alpine",
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
