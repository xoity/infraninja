import pyinfra
from pyinfra.api import deploy

#alpine
from infraninja.security.ubuntu.install_tools import install_security_tools
from infraninja.security.ubuntu.media_encryption import media_encryption_setup


@deploy('Test Security Setup')
def test_deploy():

    install_security_tools()

    media_encryption_setup()

# Execute the deploy on the VMs
pyinfra.api.deploy(
    test_deploy(),
)



