from pyinfra.api import deploy
from pyinfra.operations import server, systemd


@deploy("ClamAV Setup")
def clamav_setup():
    server.shell(name="Update ClamAV database", commands="freshclam")
    systemd.service("clamav-freshclam", running=True, enabled=True)
    systemd.service("clamav-daemon", running=True, enabled=True)
