from pyinfra.api import deploy
from pyinfra.operations import apt
from pyinfra import config

config.SUDO = True

security_tools = {
    "fail2ban": True,
    "apparmor-utils": True,
    "auditd": True,
    "clamav": True,
    "clamav-daemon": True,
    "lynis": True,
    "chkrootkit": True,
    "nmap": True,
    "suricata": True,
    "unattended-upgrades": True,
    "acl": True,
}

@deploy("Install Security Tools")
def install_security_tools():
    apt.packages(
        name="Install security tools",
        packages=[tool for tool, install in security_tools.items() if install]
    )