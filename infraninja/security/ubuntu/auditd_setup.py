from pyinfra.operations import  files, systemd
from pyinfra.api import deploy
from pyinfra import config

from infraninja.security.common.acl import acl_setup

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

    # Apply audit rules to /etc/audit/rules.d/audit.rules
    files.put(
        name="Upload custom audit.rules",
        src="rules/audit.rules",
        dest="/etc/audit/rules.d/audit.rules",
        create_remote_dir=True,
    )

    # If directly embedding rules, we can also do this inline:
    files.line(
        name="Add essential audit rules",
        path="/etc/audit/rules.d/audit.rules",
        line=audit_rules,
        replace=".*",
        present=True,
    )

    # Step 3: Ensure log rotation for auditd logs
    files.put(
        name="Upload auditd logrotate config",
        src="configs/auditd.logrotate",
        dest="/etc/logrotate.d/audit",
    )

    # Step 4: Enable and start auditd
    systemd.service(
        name="Enable and start auditd",
        service="auditd",
        running=True,
        enabled=True,
    )

    # Step 5: Restart auditd to apply new rules
    systemd.service(
        name="Restart auditd to apply new rules",
        service="auditd",
        restarted=True,
    )

    acl_setup()