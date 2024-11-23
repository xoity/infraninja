from pyinfra.operations import files, server, systemd
from pyinfra.api import deploy

@deploy("disable Media Autorun")
def media_autorun():
    systemd.service(
        name="Disable udisks2 service",
        service="autofs",
        running=False,
        enabled=False,
    )

    # Ensure the directory exists
    files.directory(
        name="Ensure /etc/udev/rules.d directory exists",
        path="/etc/udev/rules.d",
        present=True,
    )

    files.line(
        name="Disable media autorun",
        path="/etc/udev/rules.d/85-no-automount.rules",
        line="ACTION==\"add\", SUBSYSTEM==\"block\", ENV{UDISKS_AUTO}=\"0\", ENV{UDISKS_IGNORE}=\"1\"",
        present=True,
    )

    server.shell(
        name="Reload udev rules",
        commands=["udevadm control --reload-rules && udevadm trigger"],
    )

    files.line(
        name="Disable media autorun",
        path="/etc/fstab",
        line="/dev/sda1 /mnt/usb vfat noauto,nouser,noexec 0 0",
        present=True,
    )

    server.shell(
        name="reload fstab",
        commands=["mount -a"],
    )