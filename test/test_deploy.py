import pyinfra
from pyinfra.api import deploy
from infraninja.security.alpine.install_tools import install_security_tools as task1
from infraninja.security.common.ssh_hardening import ssh_hardening as task2


@deploy("Test Security Setup")
def test_deploy():
    # define any deploys & functions below! add sudo=True to any operations that require it
    task1(_sudo=True)
    task2(_sudo=True)


pyinfra.api.deploy(
    test_deploy(),
)
