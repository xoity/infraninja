from io import StringIO

from pyinfra.api import deploy
from pyinfra.operations import files


@deploy("Configure Password Policy")
def password_policy():
    # Configure login.defs
    login_defs_config = {
        "PASS_MAX_DAYS": "90",
        "PASS_MIN_DAYS": "7",
        "LOGIN_RETRIES": "3",
        "LOGIN_TIMEOUT": "60",
        "UMASK": "027",
    }

    for setting, value in login_defs_config.items():
        files.line(
            name=f"Configure {setting}",
            path="/etc/login.defs",
            line=f"{setting}\t{value}",
            replace=f"^{setting}\t.*$",  # Match the entire line starting with setting
        )

    # Configure PAM password requirements
    files.put(
        name="Configure PAM password quality settings",
        src=StringIO(
            "\n".join(
                [
                    "password requisite pam_pwquality.so retry=3",
                    "minlen=14 dcredit=-1 ucredit=-1 ocredit=-1 lcredit=-1",
                    "difok=8 maxrepeat=3 reject_username enforce_for_root",
                ]
            )
        ),
        dest="/etc/security/pwquality.conf",
        mode="644",
    )
