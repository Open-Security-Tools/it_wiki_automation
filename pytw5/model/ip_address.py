from . import interface
from typing import Optional, cast, Tuple
import ipaddress
import logging

log = logging.getLogger(__name__)


class IpAddress(interface.IPv4Address):

    def __init__(self, ipv4: str, network: Optional[interface.Network]) -> None:
        self._ipv4 = ipv4
        if network is not None:
            assert isinstance(network, interface.Network)
        self._network = network
        self._mac: Optional[interface.MacAddress] = None
        self._annotations: List[str] = []
        self._dns_lookups: List[interface.DNSLookup] = []
        log.debug(f"{self} created")

    def __repr__(self) -> str:
        return f"IpAddress(ipv4={self._ipv4}, network={self._network}) created"

    @property
    def dns_lookups(self) -> Tuple[interface.DNSLookup, ...]:
        return tuple(sorted(self._dns_lookups, key=lambda x: x.host))

    def internal_add_dns_lookup(self, value: interface.DNSLookup) -> None:
        assert value.host not in [x.host for x in self._dns_lookups]
        self._dns_lookups.append(value)

    @property
    def ipv4(self) -> str:
        return self._ipv4

    @property
    def network(self) -> Optional[interface.Network]:
        return self._network

    def internal_set_network(self, value: interface.Network) -> None:
        self._network = value

    @property
    def mac(self) -> Optional[interface.MacAddress]:
        return self._mac

    def set_mac(self, value: interface.MacAddress) -> None:
        from . import mac_address
        assert isinstance(value, mac_address.MacAddress)
        if self._mac is not None:
            assert self._mac.mac == value.mac, f"Cannot set IP address {self._ipv4} mac to {value.mac}, it is already set to {self._mac.mac}"
        else:
            value.internal_add_ip_address(value=cast(interface.MacAddress, self))
            self._mac = value

    @property
    def annotations(self) -> Tuple[str, ...]:
        # We'll pull in the mac address annotations too...
        x = []
        x.extend(self._annotations)
        if self._mac:
            x.extend(self._mac.annotations)
        return tuple(sorted(x))

    def add_annotation(self, annotation: str) -> None:
        if annotation:
            self._annotations.append(annotation)
