from pyinfra.api import deploy
from pyinfra.operations import files, openrc


@deploy("Fix and configure Fail2Ban on Alpine Linux")
def fail2ban_setup_alpine():
    # Upload Fail2Ban configuration file from template
    files.template(
        name="Upload Fail2Ban config from template",
        src="../infraninja/security/templates/alpine/fail2ban_setup_alpine.j2",
        dest="/etc/fail2ban/jail.local",
    )

    # Ensure the Fail2Ban log directory exists
    files.directory(
        name="Create Fail2Ban log directory",
        path="/var/log/fail2ban",
        present=True,
    )

    # Enable and start Fail2Ban service
    openrc.service(
        name="Enable and start Fail2Ban",
        service="fail2ban",
        running=True,
        enabled=True,
    )
