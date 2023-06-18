from abc import ABC, abstractmethod
from typing import Tuple, Optional


class DNSLookup(ABC):

    @property
    @abstractmethod
    def host(self) -> str:
        raise NotImplementedError()

    @property
    @abstractmethod
    def ip_addresses(self) -> Tuple['IPv4Address', ...]:
        raise NotImplementedError()

    @abstractmethod
    def add_ip_address(self, value: 'IPv4Address') -> None:
        raise NotImplementedError()

    @property
    @abstractmethod
    def annotations(self) -> Tuple[str, ...]:
        raise NotImplementedError()

    @abstractmethod
    def add_annotation(self, annotation: str) -> None:
        raise NotImplementedError()


class IPv4Address(ABC):

    @property
    @abstractmethod
    def ipv4(self) -> str:
        raise NotImplementedError()

    @property
    @abstractmethod
    def network(self) -> 'Network':
        raise NotImplementedError()

    @property
    @abstractmethod
    def dns_lookups(self) -> Tuple['DNSLookup', ...]:
        raise NotImplementedError()

    @property
    @abstractmethod
    def mac(self) -> Optional['MacAddress']:
        raise NotImplementedError()

    @abstractmethod
    def set_mac(self, value: 'MacAddress') -> None:
        raise NotImplementedError()

    @property
    @abstractmethod
    def annotations(self) -> Tuple[str, ...]:
        raise NotImplementedError()

    @abstractmethod
    def add_annotation(self, annotation: str) -> None:
        raise NotImplementedError()


class Network(ABC):

    @property
    @abstractmethod
    def network(self) -> str:
        raise NotImplementedError()
    
    @property
    @abstractmethod
    def prefix_length(self) -> int:
        raise NotImplementedError()

    @property
    @abstractmethod
    def vlan(self) -> Optional[int]:
        raise NotImplementedError()

    @abstractmethod
    def set_vlan(self, value: int) -> None:
        raise NotImplementedError()

    @property
    @abstractmethod
    def ip_addresses(self) -> Tuple[IPv4Address, ...]:
        raise NotImplementedError()

    @property
    @abstractmethod
    def annotations(self) -> Tuple[str, ...]:
        raise NotImplementedError()

    @abstractmethod
    def add_annotation(self, annotation: str) -> None:
        raise NotImplementedError()



class MacAddress(ABC):

    @property
    @abstractmethod
    def mac(self) -> str:
        raise NotImplementedError()

    @property
    @abstractmethod
    def ip_addresses(self) -> Tuple[IPv4Address, ...]:
        raise NotImplementedError()

    @property
    @abstractmethod
    def annotations(self) -> Tuple[str, ...]:
        raise NotImplementedError()

    @abstractmethod
    def add_annotation(self, annotation: str) -> None:
        raise NotImplementedError()


class Model(ABC):

    @property
    @abstractmethod
    def mac_addresses(self) -> Tuple[MacAddress, ...]:
        raise NotImplementedError()

    @abstractmethod
    def get_mac(self, mac: str) -> MacAddress:
        raise NotImplementedError()

    @property
    @abstractmethod
    def networks(self) -> Tuple[Network, ...]:
        raise NotImplementedError()

    @abstractmethod
    def get_network(self, network: str) -> Network:
        raise NotImplementedError()

    @property
    @abstractmethod
    def ip_addresses(self) -> Tuple[IPv4Address, ...]:
        raise NotImplementedError()

    @abstractmethod
    def get_ip_address(self, ip_address: str) -> IPv4Address:
        raise NotImplementedError()

    @property
    @abstractmethod
    def dns_lookups(self) -> Tuple[DNSLookup, ...]:
        raise NotImplementedError()

    @abstractmethod
    def get_dns_lookup(self, host: str) -> DNSLookup:
        raise NotImplementedError()
