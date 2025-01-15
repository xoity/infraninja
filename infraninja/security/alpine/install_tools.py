from pyinfra import host
from pyinfra.api import deploy
from pyinfra.facts.apk import ApkPackages
from pyinfra.operations import apk

# Define defaults for each security tool and related packages
DEFAULTS = {
    "security_tools": {
        "fail2ban": {
            "install": True,
            "packages": ["fail2ban"],
        },
        "apparmor-utils": {
            "install": True,
            "packages": ["apparmor-utils"],
        },
        "auditd": {
            "install": True,
            "packages": ["audit"],
        },
        "clamav": {
            "install": True,
            "packages": ["clamav", "clamav-daemon"],
        },
        "lynis": {
            "install": True,
            "packages": ["lynis"],
        },
        "suricata": {
            "install": True,
            "packages": ["suricata"],
        },
        "acl": {
            "install": True,
            "packages": ["acl"],
        },
        "cronie": {
            "install": True,
            "packages": ["cronie"],
        },
        "nftables": {
            "install": True,
            "packages": ["nftables"],
        },
        "ntp": {
            "install": True,
            "packages": ["ntp"],
        },
    }
}


@deploy("Install Security Tools", data_defaults=DEFAULTS)
def install_security_tools():
    # Get current package state
    try:
        installed_packages = host.get_fact(ApkPackages)
    except Exception as e:
        host.noop(
            name="Failed to get installed packages",
            warning=f"Could not determine installed packages: {str(e)}"
        )
        return

    # Loop over each tool in the host data
    for _, tool_data in host.data.security_tools.items():
        if not tool_data["install"]:
            continue

        for package in tool_data["packages"]:
            if package in installed_packages:
                host.noop(
                    name=f"Skip {package}",
                    warning=f"Package {package} is already installed"
                )
                continue

            try:
                # Attempt to install the package
                apk.packages(
                    name=f"Install {package}",
                    packages=[package],
                    present=True
                )
            except Exception as e:
                host.noop(
                    name=f"Failed to install {package}",
                    warning=f"Error installing {package}: {str(e)}"
                )
