from pyinfra import config
from pyinfra.api import deploy
from pyinfra.operations import files, systemd

config.SUDO = True

ssh_config = {
    "PermitRootLogin": "prohibit-password",
    "PasswordAuthentication": "no",
    "X11Forwarding": "no",
}


@deploy("SSH Hardening")
def ssh_hardening():
    # Track whether any changes were made
    config_changed = False

    for option, value in ssh_config.items():
        # Apply each SSH configuration setting
        change = files.replace(
            name=f"Configure SSH: {option}",
            path="/etc/ssh/sshd_config",
            text=f"^{option} .*$",
            replace=f"{option} {value}",
        )

        # If any change was detected, set `config_changed` to True
        if change.changed:
            config_changed = True

    # If any changes were made, reload and restart the SSH service
    if config_changed:
        systemd.daemon_reload()  # Reload systemd to pick up changes
        systemd.service(
            name="Restart SSH",
            service="ssh",
            running=True,
            restarted=True,
        )
