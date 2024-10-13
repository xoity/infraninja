from pyinfra.api import deploy
from pyinfra.operations import files, server

DEFAULTS = {
    "claim_token": "XXXXX",
    "claim_rooms": "XXXXX",
    "claim_url": "https://app.netdata.cloud",
    "reclaim": False,
    "dbengine_multihost_disk_space": 2048,
    "web_mode": None,
}


@deploy("Deploy Netdata", data_defaults=DEFAULTS)
def deploy_netdata():
    # Download the installation script
    files.download(
        name="Download the installation script",
        src="https://my-netdata.io/kickstart.sh",
        dest="~/kickstart.sh",
        mode="+x",
    )

    # Install Netdata
    server.shell(
        name="Install Netdata",
        commands=["~/kickstart.sh --dont-wait"],
    )

    # Cleanup installation script
    files.file(
        name="Cleanup installation script",
        path="~/kickstart.sh",
        present=False,  # equivalent to 'state: absent'
    )

    netdata_config = files.template(
        name="Template the netdata.conf file",
        src="../templates/netdata.conf.j2",
        dest="/etc/netdata/netdata.conf",
        user="root",
        group="root",
        mode="644",
    )

    # Restart Netdata service
    server.service(
        name="Restart Netdata",
        service="netdata",
        running=True,  # Ensures the service is running
        restarted=True,  # Equivalent to 'state: restarted'
        enabled=True,
        _if=netdata_config.changed,
    )