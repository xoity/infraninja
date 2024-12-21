from pyinfra import host
from pyinfra.api import deploy
from pyinfra.facts.server import LinuxName
from pyinfra.operations import files, openrc, server, systemd

os = host.get_fact(LinuxName)


@deploy("nftables Setup for Alpine Linux")
def nftables_setup_alpine():
    # Ensure the /etc/nftables directory exists
    files.directory(
        name="Create /etc/nftables directory",
        path="/etc/nftables",
        present=True,
    )

    # Upload nftables rules file
    files.template(
        name="Upload nftables rules from template",
        src="../infraninja/security/templates/nftables_rules.nft.j2",
        dest="/etc/nftables/ruleset.nft",
        mode="644",
    )

    # Apply nftables rules
    server.shell(
        name="Apply nftables rules",
        commands="nft -f /etc/nftables/ruleset.nft",
    )


# Enable nftables to restore rules on reboot based on OS
if os == "Ubuntu":
    systemd.systemd(
        name="Enable nftables service",
        service="nftables",
        running=True,
        enabled=True,
    )
elif os == "Alpine":
    openrc.service(
        name="Enable nftables service",
        service="nftables",
        running=True,
        enabled=True,
    )
