import pyinfra
from pyinfra.api import deploy

#alpine
from infraninja.security.alpine.install_tools import install_security_tools
from infraninja.security.alpine.clamav_setup import clamav_setup
from infraninja.security.alpine.fail2ban_setup import fail2ban_setup_alpine
from infraninja.security.alpine.lynis_setup import lynis_setup
from infraninja.security.alpine.suricata_setup import suricata_setup
from infraninja.security.alpine.iptables_setup import iptables_setup_alpine


@deploy('Test Security Setup')
def test_deploy():
    # Run the install_security_tools deploy
    install_security_tools()

    # Run the chkrootkit_setup deploy

    # Run the clamav_setup deploy
    clamav_setup()

    # Run the fail2ban_setup deploy
    fail2ban_setup_alpine()

    # Run the lynis_setup deploy
    lynis_setup()

    # Run the suricata_setup deploy
    suricata_setup()

    # Run the iptables_setup deploy
    iptables_setup_alpine()
    


# Execute the deploy on the VMs
pyinfra.api.deploy(
    test_deploy(),
)



