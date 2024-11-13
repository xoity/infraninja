from pyinfra import config
from pyinfra.api import deploy
from pyinfra.operations import files, server, systemd

config.SUDO = True


@deploy("Apply Routing Controls")
def routing_controls():
    systemd.service("apparmor", running=True, enabled=True)
    systemd.service("auditd", running=True, enabled=True)

    files.line(
        name="Enable positive source/destination address checks",
        path="/etc/sysctl.conf",
        line="net.ipv4.conf.all.rp_filter=1",
    )
    server.shell(name="Reload sysctl settings", commands=["sysctl -p"])
