from pyinfra.api import deploy
from pyinfra.operations import server, systemd


@deploy("Apply Routing Controls")
def routing_controls():
    systemd.service("apparmor", running=True, enabled=True)
    systemd.service("auditd", running=True, enabled=True)

    server.sysctl(
        name="Enable positive source/destination address checks",
        key="net.ipv4.conf.all.rp_filter",
        value=1,
        persist=True,
    )

    server.shell(name="Reload sysctl settings", commands=["sysctl -p"])
