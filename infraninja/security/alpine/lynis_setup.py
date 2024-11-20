from pyinfra import config
from pyinfra.api import deploy
from pyinfra.operations import files, openrc, server

from infraninja.security.common.acl import acl_setup

config.SUDO = True


@deploy("Lynis Setup")
def lynis_setup():
    # Ensure cron service is enabled and started
    openrc.service(
        name="Enable and start cron service",
        service="crond",
        running=True,
        enabled=True,
    )

    # Configure Lynis with detailed reporting
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

    # Use a local file for lynis_config_content, such as a temporary file
    with open("/tmp/lynis.cfg", "w") as f:
        f.write(lynis_config_content)

    # Upload Lynis configuration file with detailed reporting settings
    files.put(
        name="Upload Lynis configuration for detailed reporting on Alpine",
        src="/tmp/lynis.cfg",
        dest="/etc/lynis/lynis.cfg",
    )

    # Create a wrapper script for Lynis audits on Alpine
    lynis_audit_script = """#!/bin/sh
    lynis audit system --auditor "automated" > /var/log/lynis/lynis-detailed-report.txt
    """

    # Write to a temporary file for the Lynis audit script
    with open("/tmp/run_lynis_audit.sh", "w") as f:
        f.write(lynis_audit_script)

    # Upload the Lynis audit wrapper script and make it executable
    files.put(
        name="Upload Lynis audit wrapper script for Alpine",
        src="/tmp/run_lynis_audit.sh",
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
    server.shell(
        name="Create Lynis log directory for Alpine",
        commands="mkdir -p /var/log/lynis",
    )

    # Configure log rotation for Lynis reports
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

    # Write to a temporary file for logrotate configuration
    with open("/tmp/lynis_logrotate.conf", "w") as f:
        f.write(logrotate_config)

    # Apply log rotation configuration for Lynis reports on Alpine
    files.put(
        name="Upload Lynis logrotate configuration for Alpine",
        src="/tmp/lynis_logrotate.conf",
        dest="/etc/logrotate.d/lynis",
    )

    # Call ACL setup
