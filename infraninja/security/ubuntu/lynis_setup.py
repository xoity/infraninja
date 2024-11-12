from pyinfra.api import deploy
from pyinfra.operations import files, server
from pyinfra import config
from infraninja.security.common.acl import acl_setup


config.SUDO = True

@deploy("Lynis Setup")
def lynis_setup():

    # Step 2: Configure Lynis with detailed reporting

    # Define custom Lynis configuration settings inline
    lynis_config_content = """
    # Enable detailed reporting
    audit_report_detail="enabled"

    # Report and log file paths
    report_file="/var/log/lynis/lynis-report.dat"
    log_file="/var/log/lynis/lynis.log"

    # Enable full scans covering all security aspects
    scan_profile_categories="malware, authentication, network, kernel, file_system, usb, storage, software_mgmt"

    # Set verbose level to provide detailed client reports
    verbose_level=2
    """

    # Apply custom Lynis configuration directly
    files.put(
        name="Upload Lynis configuration for detailed reporting",
        src=lynis_config_content,
        dest="/etc/lynis/lynis.cfg",
    )

    # Step 3: Create a wrapper script for Lynis audits

    # Wrapper script content for running a detailed Lynis audit
    lynis_audit_script = """#!/bin/bash
    lynis audit system --auditor "automated" > /var/log/lynis/lynis-detailed-report.txt
    """

    # Upload the Lynis audit wrapper script to the server
    files.put(
        name="Upload Lynis audit wrapper script",
        src=lynis_audit_script,
        dest="/usr/local/bin/run_lynis_audit",
        mode="755",  # Make it executable
    )

    # Step 4: Set up a cron job to run the Lynis audit script weekly

    cron_line = "0 0 * * 7 root /usr/local/bin/run_lynis_audit"  # Weekly on Sundays at midnight

    # Add or ensure the cron job line exists in /etc/crontab
    files.line(
        name="Add Lynis cron job for weekly audits",
        path="/etc/crontab",
        line=cron_line,
        present=True,
    )

    # Step 5: Ensure log directory exists for Lynis
    server.shell(
        name="Create Lynis log directory",
        commands="mkdir -p /var/log/lynis",
    )

    # Step 6: Optional log rotation configuration (if needed)

    logrotate_config = """
    /var/log/lynis/lynis-detailed-report.txt {
        daily
        rotate 14
        compress
        delaycompress
        missingok
        notifempty
        postrotate
            /etc/init.d/lynis reload > /dev/null 2>&1 || true
        endscript
    }
    """

    # Apply log rotation settings for Lynis reports
    files.put(
        name="Upload Lynis logrotate configuration",
        src=logrotate_config,
        dest="/etc/logrotate.d/lynis",
    )

    acl_setup()