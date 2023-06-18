from . import interface
from typing import Tuple
import logging

log = logging.getLogger(__name__)


class DnsLookup(interface.DNSLookup):

    def __init__(self, host: str) -> None:
        self._host = host
        self._annotations: List[str] = []
        self._ip_addresses: List[interface.IPv4Address] = []
        log.debug(f"{self} created")

    def __repr__(self) -> str:
        return f"DnsLookup({self._host})"

    @property
    def host(self) -> str:
        return self._host

    @property
    def ip_addresses(self) -> Tuple[interface.IPv4Address, ...]:
        return tuple(sorted(self._ip_addresses, key=lambda x: x.ipv4))

    def add_ip_address(self, value: interface.IPv4Address) -> None:
        from . import ip_address

        # Ignore if already added
        if value.ipv4 in [x.ipv4 for x in self._ip_addresses]:
            return

        assert isinstance(value, ip_address.IpAddress)
        self._ip_addresses.append(value)
        value.internal_add_dns_lookup(self)

    @property
    def annotations(self) -> Tuple[str, ...]:
        return tuple(sorted(self._annotations))

    def add_annotation(self, annotation: str) -> None:
        if annotation:
            self._annotations.append(annotation)
