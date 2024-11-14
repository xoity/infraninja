from pyinfra.api import deploy
from pyinfra.operations import files, server
from pyinfra import config

config.SUDO = True


@deploy("chkrootkit Setup for Alpine Linux")
def chkrootkit_setup_alpine():
    # Ensure cron service is enabled and started using OpenRC
    server.shell(
        name="Enable and start cron service",
        commands="rc-update add crond default && rc-service crond start",
    )

    # Define the chkrootkit scan script
    chkrootkit_script = """#!/bin/sh
    chkrootkit > /var/log/chkrootkit/chkrootkit-scan-$(date +\\%F).log
    """

    # Upload the chkrootkit scan script to the server
    files.put(
        name="Upload chkrootkit scan script for Alpine",
        src=chkrootkit_script,
        dest="/usr/local/bin/run_chkrootkit_scan",
        mode="755",  # Make the script executable
    )

    # Schedule the chkrootkit scan with a cron job (weekly on Sundays at 2 AM)
    cron_line = "0 2 * * 0 /usr/local/bin/run_chkrootkit_scan"

    # Add or ensure the cron job line exists in /etc/crontabs/root (Alpine's cron file for root)
    files.line(
        name="Add chkrootkit cron job for weekly scans in Alpine",
        path="/etc/crontabs/root",
        line=cron_line,
        present=True,
    )

    # Ensure the log directory for chkrootkit exists
    server.shell(
        name="Create chkrootkit log directory for Alpine",
        commands="mkdir -p /var/log/chkrootkit",
    )

    # Configure log rotation for chkrootkit logs
    logrotate_config = """
    /var/log/chkrootkit/*.log {
        weekly
        rotate 4
        compress
        delaycompress
        missingok
        notifempty
        postrotate
            rc-service chkrootkit reload > /dev/null 2>&1 || true
        endscript
    }
    """

    # Apply log rotation settings for chkrootkit logs on Alpine
    files.put(
        name="Upload chkrootkit logrotate configuration for Alpine",
        src=logrotate_config,
        dest="/etc/logrotate.d/chkrootkit",
    )
