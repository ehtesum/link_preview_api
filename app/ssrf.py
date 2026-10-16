import socket
import ipaddress
from urllib.parse import urlparse

def is_safe_url(url: str) -> bool:
    """Verifies that the target URL resolves to a public, non-internal IP address to prevent SSRF."""
    try:
        parsed = urlparse(url)
        if parsed.scheme not in ('http', 'https'):
            return False

        hostname = parsed.hostname
        if not hostname:
            return False

        # Resolve hostname to IPv4/IPv6 addresses
        addr_info = socket.getaddrinfo(hostname, None)
        for _, _, _, _, sockaddr in addr_info:
            ip_str = sockaddr[0]
            ip = ipaddress.ip_address(ip_str)

            # Block internal, loopback, private, and cloud metadata (169.254.169.254) addresses
            if (
                ip.is_private or
                ip.is_loopback or
                ip.is_link_local or
                ip.is_multicast or
                ip.is_reserved or
                ip.is_unspecified
            ):
                return False

        return True
    except Exception:
        return False
