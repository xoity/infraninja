from pyinfra import config
from pyinfra.api import deploy
from pyinfra.operations import files, openrc, server

from infraninja.security.common.acl import acl_setup

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

    # Path to temporary file
    tmp_config_path = "/tmp/jail.local"
    final_config_path = "/etc/fail2ban/jail.local"

    # Write the configuration to a temporary file
    server.shell(
        name="Write Fail2Ban configuration to a temporary file",
        commands=[
            f"echo '{fail2ban_config_content.strip()}' > {tmp_config_path}",
            f"chmod 644 {tmp_config_path}",  # Ensure appropriate permissions
        ],
    )

    # Use files.put to copy the temporary file to the final location
    files.put(
        name="Copy Fail2Ban configuration to /etc/fail2ban/jail.local",
        src=tmp_config_path,
        dest=final_config_path,
        mode="644",
    )

    # Restart the Fail2Ban service
    openrc.service(
        name="Restart Fail2Ban service",
        service="fail2ban",
        restarted=True,
    )

    # Setup ACLs
    acl_setup()
