from pyinfra.api import deploy
from pyinfra.operations import systemd, openrc
from pyinfra import host, config
from pyinfra.facts.server import LinuxName, SystemdStatus, OpenRCStatus

# Get the OS type
os = host.get_fact(LinuxName)  
config.SUDO = True

# List of services to disable if present
common_services = ["avahi-daemon", "cups", "bluetooth", "rpcbind", "vsftpd", "telnet"]

@deploy('Disable useless services common')
def disable_useless_services_common():
    
    # Fetch the list of active services depending on OS
    active_services = None
    if os == 'Ubuntu':
        active_services = host.get_fact(SystemdStatus)  # Get active services for systemd
    elif os == 'Alpine':
        active_services = host.get_fact(OpenRCStatus)   # Get active services for OpenRC

    # Disable the services if they are active
    if active_services:
        for service in common_services:
            if service in active_services:
                if os == 'Ubuntu':
                    systemd.service(service, running=False, enabled=False)
                    print(f"Disabled service: {service} on Ubuntu")
                elif os == 'Alpine':
                    openrc.service(service, running=False, enabled=False)
                    print(f"Disabled service: {service} on Alpine")
            else:
                print(f"Service {service} not found on {os}, skipping.")
    else:
        print(f"No active services found or unsupported OS: {os}")
