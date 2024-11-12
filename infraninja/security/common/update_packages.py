from pyinfra import config, host
from pyinfra.api import deploy
from pyinfra.facts.server import LinuxName
from pyinfra.operations import apk, apt

os = host.get_fact(LinuxName)
config.SUDO = True


@deploy("Common System Updates")
def system_update():
    if os == "Ubuntu":
        apt.update(name="Update Ubuntu package lists")
        apt.upgrade(name="Upgrade Ubuntu packages")
    elif os == "Alpine":
        apk.update(name="Update Alpine package lists")
        apk.upgrade(name="Upgrade Alpine packages")
    else:
        raise ValueError(f"Unsupported OS: {os}")
