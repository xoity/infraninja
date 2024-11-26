
from pyinfra.operations import server
from pyinfra.api import deploy

@deploy("Reboot the system")
def reboot_system():
    server.reboot(
        name="Reboot the system",
        delay=10,  # Delay in seconds before reboot
    )