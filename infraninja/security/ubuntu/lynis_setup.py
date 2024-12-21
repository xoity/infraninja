from pyinfra.api import deploy
from pyinfra.operations import files, server


@deploy("Lynis Setup")
def lynis_setup():
    # Upload Lynis configuration file from template
    files.template(
        name="Upload Lynis configuration for detailed reporting",
        src="../infraninja/security/templates/ubuntu/lynis_setup_ubuntu.j2",
        dest="/etc/lynis/lynis.cfg",
    )

    # Upload the Lynis audit wrapper script from template and make it executable
    files.template(
        name="Upload Lynis audit wrapper script",
        src="../infraninja/security/templates/ubuntu/lynis_audit_script_ubuntu.j2",
        dest="/usr/local/bin/run_lynis_audit",
        mode="755",
    )

    # Set up a cron job to run the Lynis audit script weekly (on Sundays at midnight)
    server.crontab(
        name="Add Lynis cron job for weekly audits",
        command="/usr/local/bin/run_lynis_audit",
        user="root",
        day_of_week=7,
        hour=0,
        minute=0,
    )

    # Ensure log directory exists for Lynis
    files.directory(
        name="Create Lynis log directory",
        path="/var/log/lynis",
        present=True,
    )

    # Apply log rotation settings for Lynis reports from template
    files.template(
        name="Upload Lynis logrotate configuration",
        src="../infraninja/security/templates/ubuntu/lynis_logrotate_ubuntu.j2",
        dest="/etc/logrotate.d/lynis",
    )
