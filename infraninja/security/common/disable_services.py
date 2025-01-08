from pyinfra import host
from pyinfra.api import deploy
from pyinfra.facts.server import LinuxName
from pyinfra.operations import openrc, systemd

# Get the OS type
os = host.get_fact(LinuxName)

# List of services to disable if present
common_services = ["avahi-daemon", "cups", "bluetooth", "rpcbind", "vsftpd", "telnet"]


@deploy("Disable useless services common")
def disable_useless_services_common():
    for service in common_services:
        if os == "Ubuntu":
            service_status = host.run_shell_command(f"systemctl is-active {service}")
            if service_status.stdout.strip() == "active":
                systemd.service(service, running=False, enabled=False)
                print(f"Disabled service: {service} on Ubuntu")
            else:
                print(f"Service {service} is not active on Ubuntu")
        elif os == "Alpine":
            service_status = host.run_shell_command(f"rc-service {service} status")
            if "started" in service_status.stdout:
                openrc.service(service, running=False, enabled=False)
                print(f"Disabled service: {service} on Alpine")
            else:
                print(f"Service {service} is not active on Alpine")
        else:
            print(f"Unsupported OS: {os}, skipping service: {service}")
