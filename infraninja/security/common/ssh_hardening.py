from pyinfra import host
from pyinfra.api import deploy
from pyinfra.operations import files, systemd, openrc
from pyinfra.facts.server import LinuxName


ssh_config = {
    "PermitRootLogin": "prohibit-password",
    "PasswordAuthentication": "no",
    "X11Forwarding": "no",
}


@deploy("SSH Hardening")
def ssh_hardening():
    config_changed = False

    for option, value in ssh_config.items():
        change = files.replace(
            name=f"Configure SSH: {option}",
            path="/etc/ssh/sshd_config",
            text=rf"^#?\s*{option}.*",
            replace=f"{option} {value}",
        )
        if change.changed:
            config_changed = True

    if config_changed:
        init_systems = host.get_fact(LinuxName)

        if "Ubuntu" in init_systems:
            systemd.daemon_reload()
            systemd.service(
                name="Restart SSH",
                service="ssh",
                running=True,
                restarted=True,
            )
        elif "Alpine" in init_systems:
            openrc.service(
                name="Restart SSH",
                service="sshd",
                running=True,
                restarted=True,
            )
