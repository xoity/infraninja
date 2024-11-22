from pyinfra import config
from pyinfra.api import deploy
from pyinfra.operations import files, systemd


config.SUDO = True


@deploy("Auditd Setup")
def auditd_setup():
    # Define a set of essential audit rules
    audit_rules = """
    -w /etc/passwd -p wa -k passwd_changes
    -w /etc/shadow -p wa -k shadow_changes
    -w /etc/sudoers -p wa -k sudoers_changes
    -w /etc/ssh/sshd_config -p wa -k ssh_config_changes
    -w /var/log/auth.log -p wa -k auth_logs
    -w /bin/su -p x -k su_command
    -a always,exit -F arch=b64 -S execve -C uid!=euid -k suspicious_exec
    -a always,exit -F arch=b64 -S chmod,creat,unlink -F auid>=1000 -F auid!=4294967295 -k user_file_modifications
    """
    audit_rules_path = "/tmp/audit.rules"
    with open(audit_rules_path, "w") as f:
        f.write(audit_rules)

    # Apply audit rules to /etc/audit/rules.d/audit.rules
    files.put(
        name="Upload custom audit.rules",
        src=audit_rules_path,
        dest="/etc/audit/rules.d/audit.rules",
        create_remote_dir=True,
    )

    # Define auditd logrotate configuration
    auditd_logrotate_config = """
    /var/log/audit/audit.log {
        rotate 5
        daily
        missingok
        notifempty
        compress
        delaycompress
        postrotate
            /etc/init.d/auditd reload > /dev/null 2>&1 || true
        endscript
    }
    """
    auditd_logrotate_path = "/tmp/auditd.logrotate"
    with open(auditd_logrotate_path, "w") as f:
        f.write(auditd_logrotate_config)

    files.put(
        name="Upload auditd logrotate config",
        src=auditd_logrotate_path,
        dest="/etc/logrotate.d/audit",
    )

    systemd.service(
        name="Enable and start auditd",
        service="auditd",
        running=True,
        enabled=True,
    )

    systemd.service(
        name="Restart auditd to apply new rules",
        service="auditd",
        restarted=True,
    )
