from pyinfra.api import deploy
from pyinfra.operations import files, openrc, server


@deploy("Suricata Setup")
def suricata_setup():
    # Custom Suricata configuration content
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

    # Write Suricata config to /tmp/suricata.yaml
    suricata_config_path = "/tmp/suricata.yaml"
    with open(suricata_config_path, "w") as f:
        f.write(suricata_config)

    files.put(
        name="Upload custom Suricata configuration",
        src=suricata_config_path,
        dest="/etc/suricata/suricata.yaml",
    )

    # Ensure the Suricata log directory exists
    server.shell(
        name="Create Suricata log directory",
        commands="mkdir -p /var/log/suricata",
    )

    # Enable and start Suricata service
    openrc.service(
        name="Enable and start Suricata",
        service="suricata",
        running=True,
        enabled=True,
    )

    # Log rotation configuration content for Suricata
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

    # Write log rotation config to /tmp/suricata_logrotate.conf
    logrotate_config_path = "/tmp/suricata_logrotate.conf"
    with open(logrotate_config_path, "w") as f:
        f.write(logrotate_config)

    files.put(
        name="Upload Suricata logrotate configuration",
        src=logrotate_config_path,
        dest="/etc/logrotate.d/suricata",
    )
