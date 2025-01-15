import logging
from pyinfra.api import deploy
from pyinfra.api.exceptions import (
    DeployError,
    OperationError,
    OperationValueError,
    PyinfraError
)
from pyinfra.operations import files, openrc

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@deploy("Fix and configure Fail2Ban on Alpine Linux")
def fail2ban_setup_alpine():
    # Upload Fail2Ban configuration file from template
    files.template(
        name="Upload Fail2Ban config from template",
        src="../infraninja/security/templates/alpine/fail2ban_setup_alpine.j2",
        dest="/etc/fail2ban/jail.local",
    )

    # Ensure the Fail2Ban log directory exists
    files.directory(
        name="Create Fail2Ban log directory",
        path="/var/log/fail2ban",
        present=True,
    )

    try:
        # Enable and start Fail2Ban service
        openrc.service(
            name="Enable and start Fail2Ban",
            service="fail2ban",
            running=True,
            enabled=True,
        )
        logger.info("Fail2Ban service successfully enabled and started")

    except OperationValueError as e:
        logger.error(f"Invalid service configuration: {e}")
        # Attempt to restore default configuration
        files.template(
            name="Restore default Fail2Ban config",
            src="../infraninja/security/templates/alpine/fail2ban_setup_alpine.j2",
            dest="/etc/fail2ban/jail.local",
        )
        raise DeployError(f"Failed to configure Fail2Ban service: {e}")

    except OperationError as e:
        logger.error(f"Failed to perform service operation: {e}")
        # Try to restart the service if it's already installed
        try:
            openrc.service(
                name="Attempt to restart Fail2Ban",
                service="fail2ban",
                restarted=True,
            )
        except PyinfraError:
            logger.error("Failed to restart Fail2Ban service")
        raise DeployError(f"Failed to start Fail2Ban service: {e}")

    except PyinfraError as e:
        logger.error(f"Unexpected pyinfra error: {e}")
        # Cleanup: ensure service is stopped if setup failed
        try:
            openrc.service(
                name="Stop Fail2Ban after error",
                service="fail2ban",
                running=False,
            )
        except PyinfraError:
            pass
        raise DeployError(f"Fail2Ban setup failed: {e}")
