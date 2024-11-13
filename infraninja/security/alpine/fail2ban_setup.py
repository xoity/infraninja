from pyinfra import config
from pyinfra.api import deploy
from pyinfra.operations import files, openrc

from infraninja.security.common.acl import acl_setup

config.SUDO = True


@deploy("Fail2Ban Setup for Alpine Linux")
def fail2ban_setup_alpine():
    # Configure Fail2Ban settings in /etc/fail2ban/jail.local
    files.file(
        name="Create jail.local if it doesn't exist",
        path="/etc/fail2ban/jail.local",
        present=True,
    )

    # Ban settings in [DEFAULT] section
    files.line(
        name="Set bantime to 3600 in Fail2Ban jail.local",
        path="/etc/fail2ban/jail.local",
        line="bantime = 3600",
        replace="bantime =.*",
    )

    files.line(
        name="Set findtime to 600 in Fail2Ban jail.local",
        path="/etc/fail2ban/jail.local",
        line="findtime = 600",
        replace="findtime =.*",
    )

    files.line(
        name="Set maxretry to 5 in Fail2Ban jail.local",
        path="/etc/fail2ban/jail.local",
        line="maxretry = 5",
        replace="maxretry =.*",
    )

    # Email settings (optional)
    files.line(
        name="Set destemail in Fail2Ban jail.local",
        path="/etc/fail2ban/jail.local",
        line="destemail = root@localhost",
        replace="destemail =.*",
    )

    files.line(
        name="Set sender email in Fail2Ban jail.local",
        path="/etc/fail2ban/jail.local",
        line="sender = fail2ban@localhost",
        replace="sender =.*",
    )

    files.line(
        name="Set action to include email notification",
        path="/etc/fail2ban/jail.local",
        line="action = %(action_mwl)s",
        replace="action =.*",
    )

    # SSH protection under [sshd] section
    files.line(
        name="Enable SSH protection in Fail2Ban jail.local",
        path="/etc/fail2ban/jail.local",
        line="[sshd]",
        present=True,
    )

    files.line(
        name="Set enabled to true for SSH jail in Fail2Ban",
        path="/etc/fail2ban/jail.local",
        line="enabled = true",
        replace="enabled =.*",
        append=True,
    )

    files.line(
        name="Set port to ssh for SSH jail in Fail2Ban",
        path="/etc/fail2ban/jail.local",
        line="port = ssh",
        replace="port =.*",
        append=True,
    )

    files.line(
        name="Set logpath to sshd_log for SSH jail in Fail2Ban",
        path="/etc/fail2ban/jail.local",
        line="logpath = %(sshd_log)s",
        replace="logpath =.*",
        append=True,
    )
    # Enable and start Fail2Ban service using OpenRC on Alpine
    openrc.service(
        name="Enable and start Fail2Ban",
        service="fail2ban",
        running=True,
        enabled=True,
    )

    # Restart Fail2Ban to apply new settings
    openrc.service(
        name="Restart Fail2Ban to apply changes",
        service="fail2ban",
        restarted=True,
    )

    # Setup ACLs (from your existing acl_setup function)
    acl_setup()
