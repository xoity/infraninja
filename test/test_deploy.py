import pyinfra
from pyinfra.api import deploy
<<<<<<< HEAD
from infraninja.security.common.ssh_hardening import ssh_hardening as task1


=======
from infraninja.security.common.ssh_hardening import ssh_hardening as task
>>>>>>> parent of 87df1a6 (	new file:   infraninja/security/alpine/dns_poisoning_protection_alpine.py)

@deploy('Test Security Setup')
def test_deploy():

    # define any deploys & functions below! add sudo=True to any operations that require it
    task1(_sudo=True)
    



pyinfra.api.deploy(
    test_deploy(),
)

