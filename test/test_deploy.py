import pyinfra
from pyinfra.api import deploy

#alpine
from infraninja.security.alpine.install_tools import install_security_tools
from infraninja.security.alpine.suricata_setup import suricata_setup


@deploy('Test Security Setup')
def test_deploy():

    install_security_tools()

    suricata_setup()


# Execute the deploy on the VMs
pyinfra.api.deploy(
    test_deploy(),
)



