from pyinfra import config
from pyinfra.api import deploy
from pyinfra.operations import server, openrc

config.SUDO = True


@deploy("ClamAV Setup")
def clamav_setup():
    server.shell(name="Update ClamAV database", commands="freshclam")
    openrc.service("clamav-freshclam", running=True, enabled=True)
    openrc.service("clamav-daemon", running=True, enabled=True)
