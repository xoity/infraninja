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
    }
}


@deploy("Install Security Tools", data_defaults=DEFAULTS)
def install_security_tools():
    # Loop over each tool in the host data
    for tool, tool_data in host.data.security_tools.items():
        # Check if the tool is set to install
        if tool_data["install"]:
            installed_packages = host.get_fact(ApkPackages)
            for package in tool_data["packages"]:
                if package not in installed_packages:
                    # Install the specified package
                    apk.packages(
                        name=f"Install {package}",
                        packages=[package],
                    )
                else:
                    print(f"{package} is already installed, skipping.")
