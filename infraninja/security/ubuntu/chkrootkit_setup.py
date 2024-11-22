from pyinfra import config
from pyinfra.api import deploy
from pyinfra.operations import files, server

config.SUDO = True


@deploy("chkrootkit Setup")
def chkrootkit_setup():
    chkrootkit_script = """#!/bin/bash
    chkrootkit > /var/log/chkrootkit/chkrootkit-scan-$(date +\\%F).log
    """
    chkrootkit_script_path = "/tmp/run_chkrootkit_scan.sh"
    with open(chkrootkit_script_path, "w") as f:
        f.write(chkrootkit_script)

    # Upload the chkrootkit scan script
    files.put(
        name="Upload chkrootkit scan script",
        src=chkrootkit_script_path,
        dest="/usr/local/bin/run_chkrootkit_scan",
        mode="755",  # Make the script executable
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

    server.shell(
        name="Create chkrootkit log directory",
        commands="mkdir -p /var/log/chkrootkit",
    )

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
    logrotate_config_path = "/tmp/chkrootkit_logrotate"
    with open(logrotate_config_path, "w") as f:
        f.write(logrotate_config)

    # Apply log rotation settings for chkrootkit logs
    files.put(
        name="Upload chkrootkit logrotate configuration",
        src=logrotate_config_path,
        dest="/etc/logrotate.d/chkrootkit",
    )
