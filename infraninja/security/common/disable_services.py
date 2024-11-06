from pyinfra.api import deploy
from pyinfra.operations import systemd, openrc

common_services = ["avahi-daemon", "cups", "bluetooth", "rpcbind", "vsftpd", "telnet"] # network discovery, printing, bluetooth, rpc for NTFs, ftp, telnet

@deploy('Disable useless services common')
def disable_useless_services_common():
    for service in common_services:
        if os == 'Ubuntu':
            systemd.service(service, running=False, enabled=False)
        if os == 'Alpine':
            openrc.service(service, running=False, enabled=False)
    
