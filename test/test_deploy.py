import pyinfra
from pyinfra.api import deploy
from infraninja.security import security_setup
from infraninja.common import system_update, ssh_common_hardening, uae_ia_compliance, disable_useless_services_common
from pyinfra import host 


@deploy('Test Security Setup')
def test_deploy():
    security_setup()
    system_update()
    ssh_common_hardening()
    uae_ia_compliance()
    disable_useless_services_common()
    


# Execute the deploy on the VMs
pyinfra.api.deploy(
    test_deploy(),
)



