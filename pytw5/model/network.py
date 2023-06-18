from . import interface
from typing import Optional, Tuple
import ipaddress
import logging

log = logging.getLogger(__name__)


class Network(interface.Network):

    def __init__(self, network: str) -> None:
        self._parsed_network = ipaddress.ip_network(network)
        self._network = network
        self._vlan: Optional[int] = None
        self._ip_addresses: List[interface.IPv4Address] = []
        self._annotations: List[str] = []
        log.debug(f"{self} created")

    @property
    def prefix_length(self) -> int:
        return self._parsed_network.prefixlen

    def __repr__(self) -> str:
        return f"Network({self._network})"

    def internal_contains_ip_address(self, value: ipaddress.ip_address) -> bool:
        return value in self._parsed_network

    def internal_add_ip_address(self, value: interface.IPv4Address) -> None:
        assert value.ipv4 not in [x.ipv4 for x in self._ip_addresses]
        self._ip_addresses.append(value)

    @property
    def network(self) -> str:
        return self._network
    
    @property
    def vlan(self) -> Optional[int]:
        return self._vlan

    def set_vlan(self, value: int) -> None:
        self._vlan = value

    @property
    def ip_addresses(self) -> Tuple[interface.IPv4Address, ...]:
        return tuple(self._ip_addresses)

    @property
    def annotations(self) -> Tuple[str, ...]:
        return tuple(sorted(self._annotations))

    def add_annotation(self, annotation: str) -> None:
        if annotation:
            self._annotations.append(annotation)
