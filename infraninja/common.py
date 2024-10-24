from pyinfra.operations import apt, apk, files
from pyinfra import host
from pyinfra.api import deploy

@deploy('Common System Updates')
def system_update():
    os = host.fact.linux_name

    if os == 'Ubuntu':
        apt.update(name="Update Ubuntu package lists", sudo=True)
        apt.upgrade(name="Upgrade Ubuntu packages", sudo=True)
    elif os == 'Alpine':
        apk.update(name="Update Alpine package lists", sudo=True)
        apk.upgrade(name="Upgrade Alpine packages", sudo=True)
    
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
            line=f"{option} {value}",
            sudo=True,
        )
