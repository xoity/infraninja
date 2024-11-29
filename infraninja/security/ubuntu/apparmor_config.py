
from pyinfra.api import deploy
from pyinfra.operations import apt, systemd, files

@deploy("Configure AppArmor")
def apparmor_config():
    apt.packages(
        name="Install AppArmor packages",
        packages=["apparmor", "apparmor-utils", "apparmor-profiles"],
        update=True,
    )

    systemd.service(
        name="Enable and start AppArmor",
        service="apparmor",
        enabled=True,
        running=True,
    )

    files.line(
        name="Set AppArmor to enforcing mode",
        path="/etc/apparmor.d/tunables/global",
        line='APPARMOR=enforce',
        replace=True,
    )

    # Set all profiles to enforce mode
    files.template(
        name="Create enforce script",
        src="templates/enforce_apparmor.sh.j2",
        dest="/usr/local/bin/enforce_apparmor.sh",
        mode="755",
        create_remote_dir=True,
    )