from pyinfra.operations import apt, apk, files
from pyinfra import host, config
from pyinfra.api import deploy
from pyinfra.facts.server import LinuxName

os = host.get_fact(LinuxName)  
config.SUDO = True

@deploy('Common System Updates')
def system_update():

    if os == 'Ubuntu':
        apt.update(name="Update Ubuntu package lists")
        apt.upgrade(name="Upgrade Ubuntu packages")
    elif os == 'Alpine':
        apk.update(name="Update Alpine package lists")
        apk.upgrade(name="Upgrade Alpine packages")
    
@deploy("ssh common hardening test")
def ssh_common_hardening():

    ssh_config = {
        "PermitRootLogin": "prohibit-password",
        "PasswordAuthentication": "no",
        "X11Forwarding": "no",
    }

    # Apply SSH configuration
    for option, value in ssh_config.items():
        files.line(
            name=f"Configure SSH: {option}",
            path="/etc/ssh/sshd_config",
            line=f"{option} {value}"
        )
