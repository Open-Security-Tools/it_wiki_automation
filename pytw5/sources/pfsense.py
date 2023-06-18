"""
Description
===========

Uses the PFSense API to populate the local model of IT infrastructure.

API Documentation
=================

The API documentation is built into the PFSense UI:

UI -> System -> API -> Documentation

"""

import datetime
import os
import logging
import requests
import getpass
import click
import json
from typing import NamedTuple, Dict, Set, Any, List, Tuple
import ipaddress
from ..model import Model, MacAddress
from ..config import singleton


log = logging.getLogger(__name__)
CERT_PATH = os.path.join(os.path.dirname(__file__), "..", "root.crt")


class PFSense:

    def __init__(self, url: str, session: requests.Session, authorisation_header: Dict[str, str]) -> None:
        self._session = session
        self._url = url
        self._authorisation_header = authorisation_header

    @classmethod
    def connect(cls) -> 'PFSense':
        print(f"Connecting to: {singleton.pfsense_host}")

        session = requests.Session()
        session.verify = CERT_PATH

        headers = {
            "Authorization": f"{singleton.pfsense_client_id} {singleton.pfsense_token}"
        }

        auth = session.get(
            "{}/api/v1/status/system".format(singleton.pfsense_host),
            headers=headers,
        )
        assert auth.ok, "Auth status = {}".format(auth.status_code)
        return PFSense(
            session=session, 
            url=singleton.pfsense_host,
            authorisation_header=headers,
        )
    
    def _load_interface_macs(self, model: Model) -> Dict[str, MacAddress]:
        # We'll find out about the network interfaces first and maintain a map
        ret: Dict[str, MacAddress] = {}

        for i_name, props in self.available_interfaces.items():

            # Not all interfaces have mac addresses (VPN tunnels, for example)
            mac = props.get("mac")

            if mac:
                mac_obj = model.get_mac(mac)
                mac_obj.add_annotation(props.get("dmesg"))
                mac_obj.add_annotation(props.get("friendly"))
                mac_obj.add_annotation(props.get("description"))

                ip_address = props.get("ipaddr")
                if ip_address:
                    ip_address_obj = model.get_ip_address(ip_address)
                    ip_address_obj.set_mac(mac_obj)
                    ip_address_obj.add_annotation("PFsense Interface Address")

                ret[i_name] = mac_obj

        return ret

    def _load_local_macs_ip_addresses_and_networks_into_model(self, model: Model) -> None:
        i_name_to_mac = self._load_interface_macs(model)

        # The interfaces API contains the network information
        for interface_name, properties in self.interfaces.items():

            description = properties.get("descr")
            ip_address = properties.get("ipaddr")
            subnet = properties.get("subnet")
            interface = properties.get("if")
            vlan = ""
            interface_components = interface.split(".")
            if len(interface_components) == 2:
                vlan = interface_components[1]

            if ip_address and subnet:
                parsed_network = ipaddress.ip_network(f"{ip_address}/{subnet}", strict=False)
                network_obj = model.get_network(f"{parsed_network.network_address}/{subnet}")
                if vlan:
                    network_obj.set_vlan(int(vlan))

                network_obj.add_annotation(description)

                ip_address_obj = model.get_ip_address(ip_address)

                # We need to convert any VLAN interface suffixes
                parent_interface = interface
                if "." in parent_interface:
                    parent_interface = parent_interface.split(".")[0]

                ip_address_obj.set_mac(i_name_to_mac[parent_interface])

        # Process the virtual IP addresses
        for vip in self.virtual_ips:
            ip_address_obj = model.get_ip_address(vip["subnet"])
            ip_address_obj.add_annotation("PFsense Virtual IP")
            ip_address_obj.add_annotation(vip.get("descr"))


    def load_model(self, model: Model) -> None:
        self._load_local_macs_ip_addresses_and_networks_into_model(model)

        # The DHCP API contains the static map from MAC to IP Address
        for dhcp_interface in self.dhcp:
            for static_map in dhcp_interface.get("staticmap", list()):
                mac = static_map["mac"]
                ip_address = static_map["ipaddr"]
                if mac and ip_address:
                    # Make sure the mac exists
                    mac_obj = model.get_mac(mac)
                    mac_obj.add_annotation(static_map.get("descr"))
                
                    # We'll create an IP address entry
                    ip_address_obj = model.get_ip_address(ip_address)
                    ip_address_obj.set_mac(mac_obj)
                    ip_address_obj.add_annotation(static_map.get("descr"))


        # Build DNS lookups
        for unbound_host in self.unbound_hosts:
            host = unbound_host.get("host")
            ip = unbound_host.get("ip")
            domain = unbound_host.get("domain")
            if host and ip and domain:
                # Make sure we have an ip
                ip_address_obj = model.get_ip_address(ip)

                dns_lookup_obj = model.get_dns_lookup(f"{host}.{domain}")
                dns_lookup_obj.add_ip_address(ip_address_obj)
                dns_lookup_obj.add_annotation(unbound_host.get("descr"))

                # Process any aliases
                aliases = unbound_host.get("aliases")
                if aliases:
                    for alias in aliases.get("item", list()):
                        host = alias.get("host")
                        domain = alias.get("domain")
                        if host and domain:

                            dns_lookup_obj = model.get_dns_lookup(f"{host}.{domain}")
                            dns_lookup_obj.add_ip_address(ip_address_obj)
                            dns_lookup_obj.add_annotation(alias.get("description"))

    @property
    def unbound_hosts(self) -> List[Dict[str, Any]]:
        response = self._session.get(
            "{}/api/v1/services/unbound".format(self._url),
            headers=self._authorisation_header,
        )
        assert response.ok
        assert response.status_code == 200

        # We are going to use this to work out what to do
        return json.loads(response.text)["data"]["hosts"]        

    @property
    def interfaces(self) -> Dict[str, Any]:

        response = self._session.get(
            "{}/api/v1/interface".format(self._url),
            headers=self._authorisation_header,
        )
        assert response.ok
        assert response.status_code == 200

        # We are going to use this to work out what to do
        return json.loads(response.text)["data"]

    @property
    def available_interfaces(self) -> Dict[str, Any]:
        response = self._session.get(
            "{}/api/v1/interface/available".format(self._url),
            headers=self._authorisation_header,
        )
        assert response.ok
        assert response.status_code == 200

        # We are going to use this to work out what to do
        return json.loads(response.text)["data"]

    @property
    def virtual_ips(self) -> Dict[str, str]:
        response = self._session.get(
            "{}/api/v1/firewall/virtual_ip".format(self._url),
            headers=self._authorisation_header,
        )
        assert response.ok
        assert response.status_code == 200

        # We are going to use this to work out what to do
        return json.loads(response.text)["data"]


    @property
    def dhcp(self) -> Dict[str, str]:

        response = self._session.get(
            "{}/api/v1/services/dhcpd".format(self._url),
            headers=self._authorisation_header,
        )
        assert response.ok
        assert response.status_code == 200

        # We are going to use this to work out what to do
        return json.loads(response.text)["data"]


def load_model(model: Model) -> None:
    PFSense.connect().load_model(model)
