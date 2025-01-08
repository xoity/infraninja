from pyinfra.api import deploy
from pyinfra.operations import apt, files, server, systemd


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
        line="APPARMOR=enforce",
        replace="APPARMOR=.*",
    )

    server.shell(
        name="Reload AppArmor profiles",
        commands=[
            "for profile in /etc/apparmor.d/*; do apparmor_parser -r $profile || echo 'Failed to load $profile'; done"
        ],
    )
