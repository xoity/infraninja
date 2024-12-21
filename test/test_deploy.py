import pyinfra
from pyinfra.api import deploy
from infraninja.security.common.ssh_hardening import ssh_hardening as task1



@deploy('Test Security Setup')
def test_deploy():

    # define any deploys & functions below! add sudo=True to any operations that require it
    task1(_sudo=True)
    



pyinfra.api.deploy(
    test_deploy(),
)

