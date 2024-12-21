from pyinfra.api import deploy
from pyinfra.operations import files

@deploy("chkrootkit Setup")
def chkrootkit_setup():
    # Upload the chkrootkit scan script from template and make it executable
    files.template(
        name="Upload chkrootkit scan script",
        src="../infraninja/security/templates/chkrootkit_scan_script.j2",
        dest="/usr/local/bin/run_chkrootkit_scan",
        mode="755",
    )

    cron_line = (
        "0 2 * * 0 root /usr/local/bin/run_chkrootkit_scan"  # Weekly on Sundays at 2 AM
    )

    # Add or ensure the cron job line exists in /etc/crontab
    files.line(
        name="Add chkrootkit cron job for weekly scans",
        path="/etc/crontab",
        line=cron_line,
        present=True,
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
        src="../infraninja/security/templates/chkrootkit_logrotate.j2",
        dest="/etc/logrotate.d/chkrootkit",
    )
