from pyinfra.api import deploy
from pyinfra.operations import server
from pyinfra import config

config.SUDO = True
media = "/dev/sda1"

@deploy("Media Encryption Setup")
def media_encryption_setup():

    # Encrypt the media partition
    server.shell(
        name="Encrypt the media partition",
        commands=f"cryptsetup -y -v luksFormat {media}",
    )

    # Open the encrypted media partition
    server.shell(
        name="Open the encrypted media partition",
        commands=f"cryptsetup luksOpen {media} media",
    )

    # Create an ext4 filesystem on the encrypted media partition
    server.shell(
        name="Create an ext4 filesystem on the encrypted media partition",
        commands="mkfs.ext4 /dev/mapper/media",
    )

    # Mount the encrypted media partition
    server.shell(
        name="Mount the encrypted media partition",
        commands="mount /dev/mapper/media /media",
    )

    # Add the encrypted media partition to /etc/fstab
    server.shell(
        name="Add the encrypted media partition to /etc/fstab",
        commands='echo "/dev/mapper/media /media ext4 defaults 0 2" >> /etc/fstab',
    )