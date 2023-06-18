import json
from pyunifi.controller import Controller
from typing import NamedTuple, Tuple
from ..config import singleton
from ..model import Model


class Switch:

    def __init__(self, name: str, mac: str) -> None:
        self._name = name
        self._mac = mac
        self.ports: Dict[int, str] = dict()

    def add_port(self, port_num: int, port_name: str) -> None:
        self.ports[port_num] = port_name

    @property
    def name(self) -> str:
        return self._name

    @property
    def mac(self) -> str:
        return self._mac

    def print(self) -> None:
        print(f"Switch {self.mac} - {self.name}")
        for port_num, port_name in self.ports.items():
            print(f"  Port {port_num} = {port_name}")


class Client(NamedTuple):

    mac: str
    switch_mac: str
    switch_name: str
    switch_port_num: int
    switch_port_name: str

    def print(self) -> None:
        print(f"Client {self.mac}")
        print(f"  Switch Mac = {self.switch_mac}")
        print(f"  Switch Name = {self.switch_name}")
        print(f"  Switch Port Num = {self.switch_port_num}")
        print(f"  Switch Port Name = {self.switch_port_name}")


def load_model(model: Model) -> None:
    c = Controller(
        singleton.unifi_controller_ip,
        singleton.unifi_user,
        singleton.unifi_password,
        version="UDMP-unifiOS",
        ssl_verify=False,
    )
    mac_to_switch: Dict[str, Switch] = dict()

    for ap in c.get_aps():
        switch = Switch(
            name=ap.get("name"),
            mac=ap.get("mac")
        )
        mac_obj = model.get_mac(switch.mac)
        mac_obj.add_annotation(f"Unifi {ap.get('model')} device '{switch.name}'")

        ip_address = ap.get("config_network", {}).get("ip")
        if ip_address:
            ip_address_obj = model.get_ip_address(ip_address)
            ip_address_obj.set_mac(mac_obj)

        for port in ap.get("port_table", list()):
            switch.add_port(
                port_num=port.get("port_idx"),
                port_name=port.get("name"),
            )
        if switch.ports:
            mac_to_switch[switch.mac] = switch
            # switch.print()

        # print(json.dumps(ap, indent=4))

    # print(c.get_networks())
    clients = list()
    for client in c.get_clients():
        # Only deal with wired clients
        if client.get("is_wired"):
            # if client.get("network", "") == "3344_ceph":
            #     print(f"Ceph mac: {client['mac']}")
            # print(json.dumps(client, indent=4))
            mac = client["mac"]
            sw_mac = client.get("sw_mac")
            sw_port = client.get("sw_port")

            if mac and sw_mac and sw_port:
                switch = mac_to_switch[sw_mac]
                port_name = switch.ports[sw_port]
                clients.append(Client(
                    mac=mac,
                    switch_mac=switch.mac,
                    switch_name=switch.name,
                    switch_port_num=sw_port,
                    switch_port_name=port_name,
                ))

    for client in clients:
        model.get_mac(client.mac.lower()).add_annotation(
            f"Connected to switch {client.switch_name} port #{client.switch_port_num} - {client.switch_port_name}"
        )
