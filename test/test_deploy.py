import pyinfra
from pyinfra.api import deploy

from infraninja.security.common.update_packages import system_update as task1


@deploy("Test Security Setup")
def test_deploy():
    # define any deploys & functions below! add sudo=True to any operations that require it
    task1(_sudo=True)


pyinfra.api.deploy(
    test_deploy(),
)
