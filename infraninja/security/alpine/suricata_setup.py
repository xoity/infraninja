from pyinfra.api import deploy
from pyinfra.operations import files, openrc

@deploy("Suricata Setup")
def suricata_setup():
    # Ensure cron service is enabled and started
    openrc.service(
        name="Enable and start cron service",
        service="crond",
        running=True,
        enabled=True,
    )

    # Upload Suricata configuration file from template
    files.template(
        name="Upload custom Suricata configuration",
        src="../infraninja/security/templates/alpine/suricata_config.j2",
        dest="/etc/suricata/suricata.yaml",
    )

    # Ensure the Suricata log directory exists
    files.directory(
        name="Create Suricata log directory",
        path="/var/log/suricata",
        present=True,
    )

    # Enable and start Suricata service
    openrc.service(
        name="Enable and start Suricata",
        service="suricata",
        running=True,
        enabled=True,
    )

    # Apply log rotation configuration for Suricata reports from template
    files.template(
        name="Upload Suricata logrotate configuration",
        src="../infraninja/security/templates/alpine/suricata_logrotate.j2",
        dest="/etc/logrotate.d/suricata",
    )
