from pyinfra.api import deploy
from pyinfra.operations import server


@deploy("T3.6.3: Log privileged operations and unauthorized access attempts")
def T4_5_1_to_T4_5_4():
    # T4.5.1 - T4.5.4: Network components inventory and scanning
    server.shell(
        name="Network scanning and port checks",
        commands=["nmap -sS -sV -O -p- localhost -oN /var/log/nmap_scan.log"],
    )
