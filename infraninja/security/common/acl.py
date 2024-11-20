from pyinfra import config
from pyinfra.api import deploy
from pyinfra.operations import server

config.SUDO = True

@deploy("Set ACL")
def acl_setup():
    # Define the ACL paths and rules
    ACL_PATHS = {
        "/etc/fail2ban": "u:root:rwx",
        "/var/log/lynis-report.dat": "u:root:r",
        "/etc/audit/audit.rules": "g:root:rwx",
    }

    for path, acl_rule in ACL_PATHS.items():
        # Properly set the ACL for the specified paths
        server.shell(
            name=f"Set ACL for {path}",
            commands=[f"setfacl -m {acl_rule} {path}"],
        )