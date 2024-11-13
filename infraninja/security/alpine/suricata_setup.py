from pyinfra import config
from pyinfra.api import deploy
from pyinfra.operations import files, openrc, server

config.SUDO = True


@deploy("Suricata Setup")
def suricata_setup():
    # Custom Suricata configuration
    suricata_config = """
    # Basic logging setup for Suricata to monitor all network traffic with high verbosity
    outputs:
    - eve-log:
        enabled: yes
        filetype: regular
        filename: /var/log/suricata/eve.json
        types:
            - alert:
                payload: yes             # enable payload in logs
                payload-printable: yes   # printable (ASCII) payload
                packet: yes              # enable logging of packet in logs
                metadata: yes            # include metadata
                http: yes                # log HTTP events
                tls: yes                 # log TLS events
    """

    # Upload the custom Suricata configuration file
    files.put(
        name="Upload custom Suricata configuration",
        src=suricata_config,
        dest="/etc/suricata/suricata.yaml",
    )

    openrc.service(
        name="Enable and start Suricata",
        service="suricata",
        running=True,
        enabled=True,
    )

    server.shell(
        name="Create Suricata log directory",
        commands="mkdir -p /var/log/suricata",
    )


    logrotate_config = """
    /var/log/suricata/eve.json {
        daily
        rotate 7
        compress
        delaycompress
        missingok
        notifempty
        postrotate
            systemctl reload suricata > /dev/null 2>&1 || true
        endscript
    }
    """

    # Upload log rotation configuration for Suricata logs
    files.put(
        name="Upload Suricata logrotate configuration",
        src=logrotate_config,
        dest="/etc/logrotate.d/suricata",
    )
