from pyinfra.api import deploy
from pyinfra.operations import server
from pyinfra.facts.server import LinuxName
from pyinfra import host

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

    # Apply sysctl settings
    for key, value in sysctl_config.items():
        server.sysctl(
            name=f"Set {key} to {value}",
            key=key,
            value=value,
            persist=True,
            persist_file="/etc/sysctl.d/99-security.conf",
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