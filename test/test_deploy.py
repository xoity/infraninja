import pyinfra
from pyinfra.api import deploy
from infraninja.security.common.update_packages import system_update


@deploy("Test Security Setup")
def test_deploy():
    # define any deploys & functions below!
    system_update()


pyinfra.api.deploy(
    test_deploy(),
)
