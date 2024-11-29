import pyinfra
from pyinfra.api import deploy
from infraninja.security.common.kernel_hardening import kernel_hardening as task2
from infraninja.security.common.password_policy import password_policy as task3
from infraninja.security.ubuntu.apparmor_config import apparmor_config as task4

@deploy('Test Security Setup')
def test_deploy():

    # define any deploys & functions below! add sudo=True to any operations that require it
    task2(_sudo=True)
    task3(_sudo=True)
    task4(_sudo=True)



pyinfra.api.deploy(
    test_deploy(),
)

