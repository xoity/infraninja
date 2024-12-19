import pyinfra
from pyinfra.api import deploy
from infraninja.security.common.password_policy import password_policy as task3

@deploy('Test Security Setup')
def test_deploy():

    # define any deploys & functions below! add sudo=True to any operations that require it
    task3(_sudo=True)



pyinfra.api.deploy(
    test_deploy(),
)

