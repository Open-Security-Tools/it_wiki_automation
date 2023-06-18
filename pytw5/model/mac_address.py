from . import interface
from typing import List, Tuple
import logging

log = logging.getLogger(__name__)


class MacAddress(interface.MacAddress):

    def __init__(self, mac: str) -> None:
        self._mac = mac
        self._ip_addresses: List[interface.IPv4Address] = []
        self._annotations: List[str] = []
        log.debug(f"{self} created")
    
    def __repr__(self) -> str:
        return f"MacAddress({self._mac})"

    def internal_add_ip_address(self, value: interface.IPv4Address) -> None:
        assert isinstance(value, interface.IPv4Address)
        assert value.ipv4 not in [x.ipv4 for x in self._ip_addresses]
        self._ip_addresses.append(value)

    @property
    def mac(self) -> str:
        return self._mac

    @property
    def ip_addresses(self) -> Tuple[interface.IPv4Address, ...]:
        return tuple(sorted(self._ip_addresses, key=lambda x: x.ipv4))

    @property
    def annotations(self) -> Tuple[str, ...]:
        return tuple(sorted(self._annotations))

    def add_annotation(self, annotation: str) -> None:
        if annotation:
            self._annotations.append(annotation)
