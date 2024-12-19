
from pyinfra.api import deploy
from pyinfra.operations import server

@deploy("ARP Poisoning Protection Rules for Alpine")
def arp_poisoning_protection_alpine():
    # Enable ARP spoofing protection
    server.shell(
        name="Enable ARP spoofing protection",
        commands=[
            "echo 1 > /proc/sys/net/ipv4/conf/all/arp_ignore",
            "echo 2 > /proc/sys/net/ipv4/conf/all/arp_announce",
        ],
    )
    # Make the changes persistent across reboots
    server.shell(
        name="Make ARP spoofing protection persistent",
        commands=[
            "echo 'net.ipv4.conf.all.arp_ignore = 1' >> /etc/sysctl.conf",
            "echo 'net.ipv4.conf.all.arp_announce = 2' >> /etc/sysctl.conf",
            "sysctl -p",
        ],
    )