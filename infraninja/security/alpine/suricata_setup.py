from importlib.resources import files as resource_files
from pyinfra.api import deploy
from pyinfra.operations import files, openrc
from pyinfra import host
from pyinfra.facts.files import File, Directory


@deploy("Suricata Setup")
def suricata_setup():
    template_dir = resource_files("infraninja.security.templates.alpine")
    config_path = template_dir.joinpath("suricata_config.j2")
    logrotate_path = template_dir.joinpath("suricata_logrotate.j2")

    # Check if Suricata is installed
    if host.get_fact(File, path="/usr/bin/suricata") is None:
        host.noop("Skip Suricata setup - suricata not installed")
        return

    # Ensure config directory exists
    if host.get_fact(Directory, path="/etc/suricata") is None:
        files.directory(
            name="Create Suricata config directory",
            path="/etc/suricata",
            present=True,
            _ignore_errors=True,
        )

    # Upload Suricata configuration
    if not files.template(
        name="Upload custom Suricata configuration",
        src=str(config_path),
        dest="/etc/suricata/suricata.yaml",
    ):
        host.noop("Skip Suricata config - failed to upload configuration")

    # Create log directory
    if host.get_fact(Directory, path="/var/log/suricata") is None:
        files.directory(
            name="Create Suricata log directory",
            path="/var/log/suricata",
            present=True,
        )

    # Check and enable Suricata service
    if host.get_fact(File, path="/etc/init.d/suricata") is None:
        host.noop("Skip Suricata service - service not found")
    else:
        openrc.service(
            name="Enable and start Suricata",
            service="suricata",
            running=True,
            enabled=True,
        )

    # Setup logrotate
    if not files.template(
        name="Upload Suricata logrotate configuration",
        src=str(logrotate_path),
        dest="/etc/logrotate.d/suricata",
    ):
        host.noop("Skip logrotate setup - failed to upload configuration")

    return True
