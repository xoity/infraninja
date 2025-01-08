from pyinfra.api import deploy
from pyinfra.operations import files, server


@deploy("chkrootkit Setup")
def chkrootkit_setup():
    # Upload the chkrootkit scan script from template and make it executable
    files.template(
        name="Upload chkrootkit scan script",
        src="../infraninja/security/templates/ubuntu/chkrootkit_scan_script.j2",
        dest="/usr/local/bin/run_chkrootkit_scan",
        mode="755",
    )

    # Set up a cron job to run the chkrootkit scan script weekly (on Sundays at 2 AM)
    server.crontab(
        name="Add chkrootkit cron job for weekly scans",
        command="/usr/local/bin/run_chkrootkit_scan",
        user="root",
        day_of_week=0,
        hour=2,
        minute=0,
    )

    # Ensure log directory exists for chkrootkit
    files.directory(
        name="Create chkrootkit log directory",
        path="/var/log/chkrootkit",
        present=True,
    )

    # Apply log rotation settings for chkrootkit logs from template
    files.template(
        name="Upload chkrootkit logrotate configuration",
        src="../infraninja/security/templates/ubuntu/chkrootkit_logrotate.j2",
        dest="/etc/logrotate.d/chkrootkit",
    )
