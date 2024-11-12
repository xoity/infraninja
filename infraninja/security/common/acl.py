from pyinfra.api import deploy
from pyinfra.operations import server
from pyinfra import config

config.SUDO = True

@deploy("Set ACL")
def acl_setup():
   
   # we can add more paths to the dictionary
    ACL_PATHS = {
        '/etc/fail2ban': 'u:admin:rwx',
        '/var/log/lynis-report.dat': 'u:security:r',
        '/etc/audit/audit.rules': 'g:audit:rwx',
    }

    for path, acl_rule in ACL_PATHS.items():
        server.shell(
            name=f"Set ACL for {path}",
            commands=[f"setfacl -m {acl_rule} {path}"]
        )
