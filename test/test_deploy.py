import pyinfra
from pyinfra.api import deploy
from infraninja.security.alpine.fail2ban_setup import fail2ban_setup_alpine as task

@deploy('Test Security Setup')
def test_deploy():

    # define any deploys & functions below! add sudo=True to any operations that require it
    task(_sudo=True)



pyinfra.api.deploy(
    test_deploy(),
)

