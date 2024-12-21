from pyinfra.api import deploy
from pyinfra.operations import files, systemd


@deploy("Fail2Ban Setup")
def fail2ban_setup():
    # Upload Fail2Ban configuration file from template
    files.template(
        name="Upload Fail2Ban configuration for Ubuntu",
        src="../infraninja/security/templates/ubuntu/fail2ban_setup_ubuntu.j2",
        dest="/etc/fail2ban/jail.local",
    )

    # Enable and start the Fail2Ban service
    systemd.service(
        name="Enable and start Fail2Ban",
        service="fail2ban",
        running=True,
        enabled=True,
    )

    # Restart Fail2Ban to apply new settings
    systemd.service(
        name="Restart Fail2Ban to apply changes",
        service="fail2ban",
        restarted=True,
    )
