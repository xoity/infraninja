import pyinfra
from pyinfra.api import deploy
from infraninja.security import security_setup
from infraninja.common import system_update, ssh_common_hardening
from pyinfra import host 


@deploy('Test Security Setup and Docker')
def test_deploy():
    # Run the security setup
    security_setup()
    # Run common system updates
    system_update()
    # Run SSH hardening
    ssh_common_hardening()



# Execute the deploy on the VMs
pyinfra.api.deploy(
    test_deploy(),
)



