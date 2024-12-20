from pyinfra.api import deploy
from pyinfra.operations import files, openrc


@deploy("Lynis Setup")
def lynis_setup():
    # Ensure cron service is enabled and started
    openrc.service(
        name="Enable and start cron service",
        service="crond",
        running=True,
        enabled=True,
    )

    # Upload Lynis configuration file from template
    files.template(
        name="Upload Lynis config from template",
        src="../infraninja/security/templates/lynis_setup.j2",
        dest="/etc/lynis/lynis.cfg",
    )

    # Upload the Lynis audit wrapper script from template and make it executable
    files.template(
        name="Upload Lynis audit wrapper script for Alpine",
        src="../infraninja/security/templates/lynis_audit_script.j2",
        dest="/usr/local/bin/run_lynis_audit",
        mode="755",
    )

    # Set up a cron job to run the Lynis audit script weekly (on Sundays at midnight)
    cron_line = "0 0 * * 7 /usr/local/bin/run_lynis_audit"

    # Add or ensure the cron job line exists in /etc/crontabs/root for Alpine
    files.line(
        name="Add Lynis cron job for weekly audits in Alpine",
        path="/etc/crontabs/root",
        line=cron_line,
        present=True,
    )

    # Ensure log directory exists for Lynis
    files.directory(
        name="Create Lynis log directory for Alpine",
        path="/var/log/lynis",
        present=True,
    )

    # Apply log rotation configuration for Lynis reports from template
    files.template(
        name="Upload Lynis logrotate configuration for Alpine",
        src="../infraninja/security/templates/lynis_logrotate.j2",
        dest="/etc/logrotate.d/lynis",
    )

