from pyinfra.api import deploy
from pyinfra.operations import files, systemd


@deploy("Fail2Ban Setup")
def fail2ban_setup():
    fail2ban_config_content = """
    [DEFAULT]
    bantime = 3600
    findtime = 600
    maxretry = 5
    destemail = root@localhost
    sender = fail2ban@localhost
    action = %(action_mwl)s

    [sshd]
    enabled = true
    port = ssh
    logpath = %(sshd_log)s
    """
    fail2ban_config_path = "/tmp/jail.local"
    with open(fail2ban_config_path, "w") as f:
        f.write(fail2ban_config_content)

    # Upload Fail2Ban configuration file
    files.put(
        name="Upload Fail2Ban configuration for Ubuntu",
        src=fail2ban_config_path,
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
