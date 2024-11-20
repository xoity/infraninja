from pyinfra import config
from pyinfra.api import deploy
from pyinfra.operations import files, openrc, server


config.SUDO = True


@deploy("Fix and configure Fail2Ban on Alpine Linux")
def fail2ban_setup_alpine():
    # Define Fail2Ban configuration as a string
    fail2ban_config_content = """
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5
destemail = root@localhost
sender = fail2ban@localhost
action = %(action_mwl)s
    """
    fail2ban_config_path = "/tmp/jail.local"
    with open(fail2ban_config_path, "w") as f:
        f.write(fail2ban_config_content)

    # Upload Fail2Ban configuration file
    files.put(
        name="Upload Fail2Ban configuration for Alpine",
        src=fail2ban_config_path,
        dest="/etc/fail2ban/jail.local",
    )

    # Ensure the Fail2Ban log directory exists
    server.shell(
        name="Create Fail2Ban log directory",
        commands="mkdir -p /var/log/fail2ban",
    )

    # Enable and start Fail2Ban service

    openrc.service(
        name="Enable and start Fail2Ban",
        service="fail2ban",
        running=True,
        enabled=True,
    )

