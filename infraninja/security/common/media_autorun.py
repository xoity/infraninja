from pyinfra.operations import files, server


def disable_usb_autorun():
    blacklist_usb_modules = [
        "usb_storage",  # Disable USB storage driver
        "usbhid",  # Disable USB human interface devices (keyboards, mice)
        "usbcore",  # Disable the USB core module
    ]

    for module in blacklist_usb_modules:
        files.append(
            name=f"Blacklist {module} module",
            src=f"/etc/modprobe.d/{module}.conf",
            dest=f"/etc/modprobe.d/{module}.conf",
            content=f"blacklist {module}\n",
            sudo=True,
        )

    server.shell(
        name="Disable USB modules immediately",
        commands="modprobe -r usb_storage usbhid usbcore",
        sudo=True,
    )

    # Modify udev rules to disable automounting
    udev_rules = """
# Disable automount for USB drives
ACTION=="add", KERNEL=="sd[b-z][0-9]", RUN+="/bin/sh -c 'exit 0'"
    """

    files.put(
        name="Upload udev rule to disable USB automount",
        src=udev_rules,
        dest="/etc/udev/rules.d/00-usb-autoset.rules",
        sudo=True,
    )

    # GNOME's autorun settings can be changed via dconf
    server.shell(
        name="Disable autorun for GNOME (if installed)",
        commands='dconf write /org/gnome/desktop/media-handling/automount "false"',
        sudo=True,
    )

    # Ensure the system won't automatically run any programs from USB devices
    files.append(
        name="Disable autorun for USB devices",
        src="/etc/udev/rules.d/99-no-autorun.rules",
        dest="/etc/udev/rules.d/99-no-autorun.rules",
        content='ACTION=="add", SUBSYSTEM=="block", ENV{ID_FS_TYPE}=="vfat|ntfs", RUN+="/bin/sh -c \'exit 0\'"',
        sudo=True,
    )

    server.shell(
        name="Reload udev rules",
        commands="udevadm control --reload",
        sudo=True,
    )

    fstab_config = """
# Disable automount for removable media
UUID=none /media auto noauto 0 0
    """

    files.append(
        name="Add fstab entry to disable automount",
        src=fstab_config,
        dest="/etc/fstab",
        content=fstab_config,
        sudo=True,
    )
