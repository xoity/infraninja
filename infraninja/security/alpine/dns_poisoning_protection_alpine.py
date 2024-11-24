from pyinfra.api import deploy
from pyinfra.operations import server, files

@deploy("DNS Poisoning Protection Rules for Alpine")
def dns_poisoning_protection_alpine():
    # Create a basic named.conf file if it does not exist
    files.line(
        name="Ensure /etc/bind/named.conf exists",
        path="/etc/bind/named.conf",
        line='include "/etc/bind/named.conf.options";',
    )

    # Create a basic named.conf.options file if it does not exist
    files.line(
        name="Ensure /etc/bind/named.conf.options exists",
        path="/etc/bind/named.conf.options",
        line="options {};",
    )

    # Configure DNSSEC in named.conf.options
    server.shell(
        name="Configure DNSSEC in /etc/bind/named.conf.options",
        commands=[
            r"sed -i '/options {/a \\    dnssec-validation auto;' /etc/bind/named.conf.options",
            r"sed -i '/options {/a \\    dnssec-enable yes;' /etc/bind/named.conf.options"
        ],
    )

    # Validate the Bind configuration before restarting
    server.shell(
        name="Validate Bind configuration",
        commands=["named-checkconf"],
    )

    # Restart the named service
    server.shell(
        name="Restart named service",
        commands=["rc-service named restart"],
    )
