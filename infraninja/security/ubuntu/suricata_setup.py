from pyinfra.api import deploy
from pyinfra.operations import files, systemd


@deploy("Suricata Setup")
def suricata_setup():
    # Upload Suricata configuration file from template
    files.template(
        name="Upload custom Suricata configuration",
        src="../infraninja/security/templates/ubuntu/suricata_config.j2",
        dest="/etc/suricata/suricata.yaml",
    )

    # Ensure the Suricata log directory exists
    files.directory(
        name="Create Suricata log directory",
        path="/var/log/suricata",
        present=True,
    )

    # Enable and start Suricata service
    systemd.service(
        name="Enable and start Suricata",
        service="suricata",
        running=True,
        enabled=True,
    )

    # Apply log rotation configuration for Suricata reports from template
    files.template(
        name="Upload Suricata logrotate configuration",
        src="../infraninja/security/templates/ubuntu/suricata_logrotate.j2",
        dest="/etc/logrotate.d/suricata",
    )
