from . import interface
from .mac_address import MacAddress
from .network import Network
from .ip_address import IpAddress
from .dns_lookup import DnsLookup
from typing import Dict, cast, Optional, Tuple
import ipaddress


class Model(interface.Model):

    def __init__(self) -> None:
        self._mac_lookup: Dict[str, MacAddress] = {}
        self._network_lookup: Dict[str, Network] = {}
        self._ip_address_lookup: Dict[str, IpAddress] = {}
        self._dns_lookups: Dict[str, DnsLookup] = {}

    @property
    def mac_addresses(self) -> Tuple[interface.MacAddress, ...]:
        return tuple(self._mac_lookup.values())

    def get_mac(self, mac: str) -> interface.MacAddress:
        assert mac == mac.lower()
        try:
            return cast(interface.MacAddress, self._mac_lookup[mac])
        except KeyError:
            m = MacAddress(mac=mac)
            self._mac_lookup[mac] = m
            return cast(interface.MacAddress, m)

    @property
    def networks(self) -> Tuple[interface.Network, ...]:
        return tuple(self._network_lookup.values())

    def get_network(self, network: str) -> interface.Network:
        try:
            return cast(interface.Network, self._network_lookup[network])
        except KeyError:
            n = Network(network)
            self._network_lookup[network] = n
            # Capture IP addresses
            for ip_address in self._ip_address_lookup.values():
                if n.internal_contains_ip_address(ipaddress.ip_address(ip_address.ipv4)):
                    ip_address.internal_set_network(n)
                    n.internal_add_ip_address(ip_address)

            return cast(interface.Network, n)

    def internal_find_network(self, ip_address: str) -> Optional[Network]:
        i = ipaddress.ip_address(ip_address)
        for n in self._network_lookup.values():
            if n.internal_contains_ip_address(i):
                return n
        return None

    @property
    def ip_addresses(self) -> Tuple[interface.IPv4Address, ...]:
        return tuple(self._ip_address_lookup.values())

    def get_ip_address(self, ip_address: str) -> interface.IPv4Address:
        try:
            return cast(interface.IPv4Address, self._ip_address_lookup[ip_address])
        except KeyError:
            # Find the network...
            n = self.internal_find_network(ip_address)
            i = IpAddress(ipv4=ip_address, network=n)
            if n:
                n.internal_add_ip_address(i)
            self._ip_address_lookup[ip_address] = i
            return cast(interface.IPv4Address, i)

    @property
    def dns_lookups(self) -> Tuple[interface.DNSLookup]:
        return tuple(self._dns_lookups.values())

    def get_dns_lookup(self, host: str) -> interface.DNSLookup:
        try:
            return cast(interface.DNSLookup, self._dns_lookups[host])
        except KeyError:
            d = DnsLookup(host)
            self._dns_lookups[host] = d
            return cast(interface.DNSLookup, d)


def create_model() -> interface.Model:
    return cast(interface.Model, Model())
