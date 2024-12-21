from pyinfra.api import deploy
from pyinfra.operations import files, systemd

@deploy("Auditd Setup")
def auditd_setup():
    # Upload auditd rules from template
    files.template(
        name="Upload custom audit.rules",
        src="../infraninja/security/templates/ubuntu/auditd_rules.j2",
        dest="/etc/audit/rules.d/audit.rules",
        create_remote_dir=True,
    )

    # Apply log rotation configuration for auditd from template
    files.template(
        name="Upload auditd logrotate config",
        src="../infraninja/security/templates/ubuntu/auditd_logrotate.j2",
        dest="/etc/logrotate.d/audit",
    )

    systemd.service(
        name="Enable and start auditd",
        service="auditd",
        running=True,
        enabled=True,
    )

    systemd.service(
        name="Restart auditd to apply new rules",
        service="auditd",
        restarted=True,
    )
