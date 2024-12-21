from pyinfra.api import deploy
from pyinfra.operations import server


@deploy("Set ACL")
def acl_setup():
    # Define the ACL paths and rules
    ACL_PATHS = {
        "/etc/fail2ban": "u:root:rwx",
        "/var/log/lynis-report.dat": "u:root:r",
        "/etc/audit/audit.rules": "g:root:rwx",
        "/etc/suricata/suricata.yaml": "u:root:rwx",
        "/var/log/suricata": "u:root:rwx",
        "/etc/iptables/rules.v4": "u:root:rwx",
        "/etc/ssh/sshd_config": "u:root:rw",
        "/etc/cron.d": "u:root:rwx",
        "/etc/rsyslog.conf": "u:root:rw",
        "/etc/modprobe.d": "u:root:rwx",
        "/etc/udev/rules.d": "u:root:rwx",
        "/etc/fstab": "u:root:rw",
    }

    for path, acl_rule in ACL_PATHS.items():
        # Properly set the ACL for the specified paths
        server.shell(
            name=f"Set ACL for {path}",
            commands=[f"setfacl -m {acl_rule} {path}"],
        )
