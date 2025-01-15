from pyinfra.api import deploy
from pyinfra.operations import files, openrc
from pyinfra import host
from pyinfra.facts.files import File, Directory

@deploy("Suricata Setup")
def suricata_setup():
    # Check if Suricata is installed
    if not host.get_fact(File("/usr/bin/suricata")):
        host.noop(
            name="Skip Suricata setup - suricata not installed",
            warning="Suricata is not installed on the system"
        )
        return

    else:
        openrc.service(
            name="Enable and start cron service",
            service="crond",
            running=True,
            enabled=True,
        )

    # Ensure config directory exists
    if not host.get_fact(Directory("/etc/suricata")):
        files.directory(
            name="Create Suricata config directory",
            path="/etc/suricata",
            present=True,
        )

    # Upload Suricata configuration
    try:
        files.template(
            name="Upload custom Suricata configuration",
            src="../infraninja/security/templates/alpine/suricata_config.j2",
            dest="/etc/suricata/suricata.yaml",
        )
    except Exception as e:
        host.noop(
            name="Failed to upload Suricata config",
            warning=f"Error uploading configuration: {str(e)}"
        )

    # Create log directory
    if not host.get_fact(Directory("/var/log/suricata")):
        files.directory(
            name="Create Suricata log directory",
            path="/var/log/suricata",
            present=True,
        )

    # Check and enable Suricata service
    if not host.get_fact(File("/etc/init.d/suricata")):
        host.noop(
            name="Skip Suricata service setup",
            warning="Suricata service not found"
        )
    else:
        openrc.service(
            name="Enable and start Suricata",
            service="suricata",
            running=True,
            enabled=True,
        )

    # Setup logrotate with error handling
    try:
        files.template(
            name="Upload Suricata logrotate configuration",
            src="../infraninja/security/templates/alpine/suricata_logrotate.j2",
            dest="/etc/logrotate.d/suricata",
        )
    except Exception as e:
        host.noop(
            name="Failed to setup logrotate",
            warning=f"Error setting up logrotate: {str(e)}"
        )
