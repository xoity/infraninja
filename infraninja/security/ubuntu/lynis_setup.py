from pyinfra.api import deploy
from pyinfra.operations import files, server


@deploy("Lynis Setup")
def lynis_setup():
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
    lynis_config_path = "/tmp/lynis.cfg"
    with open(lynis_config_path, "w") as f:
        f.write(lynis_config_content)

    # Apply custom Lynis configuration directly
    files.put(
        name="Upload Lynis configuration for detailed reporting",
        src=lynis_config_path,
        dest="/etc/lynis/lynis.cfg",
    )

    # Wrapper script content for running a detailed Lynis audit
    lynis_audit_script = """#!/bin/bash
    lynis audit system --auditor "automated" > /var/log/lynis/lynis-detailed-report.txt
    """
    lynis_audit_script_path = "/tmp/run_lynis_audit.sh"
    with open(lynis_audit_script_path, "w") as f:
        f.write(lynis_audit_script)

    # Upload the Lynis audit wrapper script to the server
    files.put(
        name="Upload Lynis audit wrapper script",
        src=lynis_audit_script_path,
        dest="/usr/local/bin/run_lynis_audit",
        mode="755",  # Make it executable
    )

    cron_line = (
        "0 0 * * 7 root /usr/local/bin/run_lynis_audit"  # Weekly on Sundays at midnight
    )

    # Add or ensure the cron job line exists in /etc/crontab
    files.line(
        name="Add Lynis cron job for weekly audits",
        path="/etc/crontab",
        line=cron_line,
        present=True,
    )

    server.shell(
        name="Create Lynis log directory",
        commands="mkdir -p /var/log/lynis",
    )

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
    logrotate_config_path = "/tmp/lynis_logrotate"
    with open(logrotate_config_path, "w") as f:
        f.write(logrotate_config)

    # Apply log rotation settings for Lynis reports
    files.put(
        name="Upload Lynis logrotate configuration",
        src=logrotate_config_path,
        dest="/etc/logrotate.d/lynis",
    )
