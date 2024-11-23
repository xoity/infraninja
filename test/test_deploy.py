import pyinfra
from pyinfra.api import deploy
from infraninja.security.ubuntu.media_autorun import media_autorun as ac

@deploy('Test Security Setup')
def test_deploy():

    # define any deploys & functions below! add sudo=True to any operations that require it
    ac(_sudo=True)



pyinfra.api.deploy(
    test_deploy(),
)

