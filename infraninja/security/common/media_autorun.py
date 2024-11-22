from pyinfra.operations import files, server
import os


blacklist_usb_modules = [
    "usb_storage",  # Disable USB storage driver
    "usbhid",  # Disable USB human interface devices (keyboards, mice)
]

for module in blacklist_usb_modules:
    # Create the temporary file with the blacklist content
    temp_file_path = f"/tmp/{module}.conf"
    with open(temp_file_path, "w") as f:
        f.write(f"blacklist {module}\n")

    # Ensure the file exists before attempting to upload
    if os.path.exists(temp_file_path):
        files.put(
            name=f"Blacklist {module} module",
            src=temp_file_path,
            dest=f"/etc/modprobe.d/{module}.conf",
        )
    else:
        print(f"Error: {temp_file_path} does not exist")

server.shell(
    name="Disable USB modules immediately",
    commands="modprobe -r usb_storage usbhid",
)

# Modify udev rules to disable automounting
udev_rules = """
# Disable automount for USB drives
ACTION=="add", KERNEL=="sd[b-z][0-9]", RUN+="/bin/sh -c 'exit 0'"
"""

# Write udev rules to a temporary file
udev_rules_path = "/tmp/00-usb-autoset.rules"
with open(udev_rules_path, "w") as f:
    f.write(udev_rules)

# Upload the udev rules file
files.put(
    name="Upload udev rule to disable USB automount",
    src=udev_rules_path,
    dest="/etc/udev/rules.d/00-usb-autoset.rules",
)


# Ensure the system won't automatically run any programs from USB devices
autorun_rules = """
ACTION=="add", SUBSYSTEM=="block", ENV{ID_FS_TYPE}=="vfat|ntfs", RUN+="/bin/sh -c 'exit 0'"
"""

# Write autorun rules to a temporary file
autorun_rules_path = "/tmp/99-no-autorun.rules"
with open(autorun_rules_path, "w") as f:
    f.write(autorun_rules)

# Upload the autorun rules file
files.put(
    name="Disable autorun for USB devices",
    src=autorun_rules_path,
    dest="/etc/udev/rules.d/99-no-autorun.rules",
)

server.shell(
    name="Reload udev rules",
    commands="udevadm control --reload",
)

fstab_config = """
# Disable automount for removable media
UUID=none /media auto noauto 0 0
"""

# Append fstab entry to disable automount
files.line(
    name="Add fstab entry to disable automount",
    path="/etc/fstab",
    line=fstab_config.strip(),
)
