from pyinfra.api import deploy
from pyinfra.operations import files, openrc, server
from pyinfra import host
from pyinfra.facts.files import File, Directory


@deploy("Lynis Setup")
def lynis_setup():
    # Check if Lynis is installed
    if not host.get_fact(File("/usr/bin/lynis")):
        host.noop(
            name="Skip Lynis setup - lynis not installed",
            warning="Lynis is not installed on the system"
        )
        return

    # Check and enable cron service
    if not host.get_fact(File("/etc/init.d/crond")):
        host.noop(
            name="Skip cron setup - crond service not found",
            warning="Cron service not found"
        )
    else:
        openrc.service(
            name="Enable and start cron service",
            service="crond",
            running=True,
            enabled=True,
        )

    # Ensure config directory exists
    if not host.get_fact(Directory("/etc/lynis")):
        files.directory(
            name="Create Lynis config directory",
            path="/etc/lynis",
            present=True,
        )

    # Upload configuration files with error handling
    config_files = [
        {
            "name": "Upload Lynis config",
            "src": "../infraninja/security/templates/alpine/lynis_setup.j2",
            "dest": "/etc/lynis/lynis.cfg"
        },
        {
            "name": "Upload Lynis audit wrapper script",
            "src": "../infraninja/security/templates/alpine/lynis_audit_script.j2",
            "dest": "/usr/local/bin/run_lynis_audit",
            "mode": "755"
        }
    ]

    for config in config_files:
        try:
            files.template(
                name=config["name"],
                src=config["src"],
                dest=config["dest"],
                mode=config.get("mode"),
                )
        except Exception as e:
            host.noop(
                name=f"Failed to upload {config['dest']}",
                warning=f"Error uploading configuration: {str(e)}"
            )

    # Set up cron job with error handling
    try:
        server.crontab(
            name="Add Lynis cron job for weekly audits",
            command="/usr/local/bin/run_lynis_audit",
            user="root",
            day_of_week=7,
            hour=0,
            minute=0,
        )
    except Exception as e:
        host.noop(
            name="Failed to setup cron job",
            warning=f"Error setting up cron job: {str(e)}"
        )

    # Create log directory
    if not host.get_fact(Directory("/var/log/lynis")):
        files.directory(
            name="Create Lynis log directory",
            path="/var/log/lynis",
            present=True,
        )

    # Setup logrotate with error handling
    try:
        files.template(
            name="Upload Lynis logrotate configuration",
            src="../infraninja/security/templates/alpine/lynis_logrotate.j2",
            dest="/etc/logrotate.d/lynis",
        )
    except Exception as e:
        host.noop(
            name="Failed to setup logrotate",
            warning=f"Error setting up logrotate: {str(e)}"
        )
