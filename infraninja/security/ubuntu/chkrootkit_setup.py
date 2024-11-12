from pyinfra.api import deploy
from pyinfra.operations import files, server
from pyinfra import config

config.SUDO = True

@deploy("chkrootkit Setup")
def chkrootkit_setup():
    chkrootkit_script = """#!/bin/bash
    chkrootkit > /var/log/chkrootkit/chkrootkit-scan-$(date +\\%F).log
    """

    # Upload the chkrootkit scan script
    files.put(
        name="Upload chkrootkit scan script",
        src=chkrootkit_script,
        dest="/usr/local/bin/run_chkrootkit_scan",
        mode="755",  # Make the script executable
    )

    # Step 3: Schedule the chkrootkit scan with a cron job

    cron_line = "0 2 * * 0 root /usr/local/bin/run_chkrootkit_scan"  # Weekly on Sundays at 2 AM

    # Add or ensure the cron job line exists in /etc/crontab
    files.line(
        name="Add chkrootkit cron job for weekly scans",
        path="/etc/crontab",
        line=cron_line,
        present=True,
    )

    # Step 4: Ensure log directory for chkrootkit exists
    server.shell(
        name="Create chkrootkit log directory",
        commands="mkdir -p /var/log/chkrootkit",
    )

    # Step 5: Configure log rotation for chkrootkit logs

    logrotate_config = """
    /var/log/chkrootkit/*.log {
        weekly
        rotate 4
        compress
        delaycompress
        missingok
        notifempty
        postrotate
            /etc/init.d/chkrootkit reload > /dev/null 2>&1 || true
        endscript
    }
    """

    # Apply log rotation settings for chkrootkit logs
    files.put(
        name="Upload chkrootkit logrotate configuration",
        src=logrotate_config,
        dest="/etc/logrotate.d/chkrootkit",
    )