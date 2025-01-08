from pyinfra.api import deploy
from pyinfra.operations import server


# When calling this deploy function, you can pass a boolean value to the need_reboot parameter
@deploy("Reboot the system")
def reboot_system(need_reboot=None):
    if need_reboot is None or need_reboot:
        server.reboot(
            name="Reboot the system",
            delay=10,  # Delay in seconds before reboot
        )
