import socket
from typing import Iterable, Tuple, Union, List
from ipaddress import ip_address, ip_network

# socket.herror error numbers
# http://sourceware.org/git/?p=glibc.git;a=blob;f=resolv/netdb.h#l62
_ERRNO_HOST_NOT_FOUND = 1
_ERRNO_TRY_AGAIN = 2
_ERRNO_NO_RECOVERY = 3
_ERRNO_NO_DATA = 4

# Which errnos to retry on, and which to return the _NOT_FOUND_RESPONSE
# response for
_HERROR_RETRY_ERRNOS = (_ERRNO_TRY_AGAIN, _ERRNO_NO_RECOVERY)
_HERROR_NOTFOUND_ERRNOS = (_ERRNO_HOST_NOT_FOUND, _ERRNO_NO_DATA)

_GAIERROR_RETRY_ERRNOS = (
    socket.EAI_AGAIN,
    socket.EAI_FAIL,
    socket.EAI_MEMORY,
    socket.EAI_SYSTEM,
    socket.EAI_OVERFLOW,
)
_GAIERROR_NOTFOUND_ERRNOS = (socket.EAI_NONAME,)

_NOT_FOUND_RESPONSE = (None, None, None)


def _gethostbyaddr(
    ip: str, max_tries: int = 1
) -> Union[Tuple[str, List[str], List[str]], Tuple[None, None, None]]:
    """
    socket.gethostbyaddr with automatic retries on transient errors.

    Returns (None, None ,None) instead of raising exceptions if the
    host cannot be found.
    """
    try:
        return socket.gethostbyaddr(ip)
    except socket.herror as e:
        errno, message = e.args
        if errno in _HERROR_NOTFOUND_ERRNOS:
            return _NOT_FOUND_RESPONSE
        elif errno in _HERROR_RETRY_ERRNOS and max_tries > 1:
            return _gethostbyaddr(ip, max_tries - 1)
        else:
            raise
    except socket.gaierror as e:
        errno, message = e.args
        if errno in _GAIERROR_NOTFOUND_ERRNOS:
            return _NOT_FOUND_RESPONSE
        elif errno in _GAIERROR_RETRY_ERRNOS and max_tries > 1:
            return _gethostbyaddr(ip, max_tries - 1)
        else:
            raise


def get_hostname_by_ip(ip: str, max_tries: int = 1) -> str:
    """
    Perform a reverse DNS lookup for a given IP.

    Returns None if the hostname cannot be determined.

    :param str ip:
    :param int max_tries: The maximum number of tries in case of
        transient network errors.
    :return: the hostname determined by rDNS.
    """
    name, _, _ = _gethostbyaddr(ip, max_tries)
    return name


def get_ips_by_hostname(hostname: str, max_tries: int = 1) -> List[str]:
    """
    Fetch the reported IP list for a given host.

    Returns None if the IPs cannot be determined.

    :param str hostname:
    :param int max_tries: The maximum number of tries in case of
        transient network errors.
    :return: the IP list reported by the host
    """
    _, _, ips = _gethostbyaddr(hostname, max_tries)
    return ips


def fcrdns_hosts(
    ip: str, allowed_hosts: Iterable[str] = None, max_tries: int = 1
) -> bool:
    """
    Verify an IP via forward-confirmed reverse DNS (FCrDNS) query.

    Optionally only allow hosts from a whitelist.

    :param str ip: An IP (v4 or v6)
    :param Iterable[str] allowed_hosts: An optional lists of allowed
        hosts that the ip is allowed to resolve to. If not provided, a
        simple FCrDNS will be performed without restricting to a subset
        of hosts.
    :param int max_tries: The maximum number of tries allowed to perform
        the FCrDNS check before raising the underlying error. Allowing
        retries can help against network instability.

    :return bool: Whether the IP is verified against the hosts
    """
    name = get_hostname_by_ip(ip, max_tries)
    if name is None:
        return False

    if allowed_hosts is not None:
        if not any((name.endswith(h) for h in allowed_hosts)):
            return False

    ips = get_ips_by_hostname(name, max_tries)
    if ips is None:
        return False

    return ip in ips


def ip_list(ip: str, allowed_ips: Iterable[str]) -> bool:
    """
    Verify an IP with an IP whitelist.

    :param str ip: an IP (v4 or v6)
    :param Iterable[str] allowed_ips: Whitelist of IPs

    :return: Whether the IP is one of the allowed IPs
    """
    return ip in allowed_ips


def ip_ranges(ip: str, allowed_ranges: Iterable[Tuple[str, str]]) -> bool:
    """
    Verify that an IP falls within one of the allowed IP ranges.

    :param str ip: an IP (v4 or v6)
    :param Iterable[Tuple[str, str]] allowed_ranges: List of allowed
        IP ranges in the form (lowest_ip, highest_ip). Bounds are
        inclusive.

    :return: Whether the IP falls within one of the allowed ranges
    """
    ipa = ip_address(ip)
    return any(
        (ip_address(rng[0]) <= ipa <= ip_address(rng[1]) for rng in allowed_ranges)
    )


def cidr_list(ip: str, allowed_cidrs: Iterable[str]) -> bool:
    """
    Verify that an IP falls within one of the allowed CIDR blocks.

    :param str ip: an IP (v4 or v6)
    :param Iterable[str] allowed_cidrs: List of allowed IP blocks

    :return: Whether the IP falls within one of the allowed CIDR blocks
    """
    return any((ip_address(ip) in ip_network(cidr) for cidr in allowed_cidrs))
