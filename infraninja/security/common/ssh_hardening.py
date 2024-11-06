# security/common/ssh_hardening.py

from pyinfra.operations import files
from pyinfra.api import deploy

ssh_config = {
    "PermitRootLogin": "prohibit-password",
    "PasswordAuthentication": "no",
    "X11Forwarding": "no",
}

@deploy("SSH Hardening")
def ssh_hardening():
    for option, value in ssh_config.items():
        files.replace(
            name=f"Configure SSH: {option}",
            path="/etc/ssh/sshd_config",
            line=f"^{option} .*$",
            replace=f"{option} {value}",
        )
