from pyinfra.api import deploy
from pyinfra.operations import files, server
from pyinfra.facts.server import LinuxName
from pyinfra import host
import tempfile

@deploy("Kernel Security Hardening")
def kernel_hardening():
    # Kernel hardening configuration
    sysctl_config = {
        # Network Security
        "net.ipv4.conf.all.accept_redirects": "0",
        "net.ipv4.conf.default.accept_redirects": "0",
        "net.ipv4.conf.all.secure_redirects": "0",
        "net.ipv4.conf.default.secure_redirects": "0",
        "net.ipv4.conf.all.accept_source_route": "0",
        "net.ipv4.conf.default.accept_source_route": "0",
        "net.ipv4.conf.all.send_redirects": "0",
        "net.ipv4.conf.default.send_redirects": "0",
        "net.ipv4.icmp_echo_ignore_broadcasts": "1",
        "net.ipv4.tcp_syncookies": "1",
        "net.ipv4.tcp_max_syn_backlog": "2048",
        "net.ipv4.tcp_synack_retries": "2",
        "net.ipv4.tcp_syn_retries": "5",
        
        # Memory Protection
        "kernel.randomize_va_space": "2",
        "vm.mmap_min_addr": "65536",
        "kernel.exec-shield": "1",
        
        # Core Dumps
        "fs.suid_dumpable": "0",
        
        # System Security
        "kernel.sysrq": "0",
        "kernel.core_uses_pid": "1",
        "kernel.dmesg_restrict": "1",
        "kernel.kptr_restrict": "2",
        "kernel.yama.ptrace_scope": "1",
    }

    # Create a temporary file
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
        for param, value in sysctl_config.items():
            temp_file.write(f"{param} = {value}\n")
        temp_path = temp_file.name

    # Upload the configuration file
    files.put(
        name="Configure sysctl security settings",
        src=temp_path,
        dest="/etc/sysctl.d/99-security.conf",
        mode="644",
    )

    # Clean up the temporary file
    server.shell(
        name="Clean up temporary file",
        commands=[f"rm -f {temp_path}"],
    )

    # Get the Linux distribution
    linux_name = host.get_fact(LinuxName)
    
    if "Alpine" in linux_name:
        server.shell(
            name="Apply sysctl settings",
            commands=["sysctl -p /etc/sysctl.d/99-security.conf"],
        )
    else:
        server.shell(
            name="Apply sysctl settings",
            commands=["sysctl --system"],
        )