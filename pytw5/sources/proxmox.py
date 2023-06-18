from proxmoxer import ProxmoxAPI
from ..config import singleton
from typing import Dict
from .. import Model


def load_model(model: Model) -> None:
    p = ProxmoxAPI(
        singleton.proxmox_host,
        user=singleton.proxmox_user, 
        password=singleton.proxmox_password, 
        verify_ssl=False
    )

    for node in p.nodes.get():
        for vm in p.nodes(node["node"]).qemu.get():
            config = p.nodes(node["node"]).qemu(vm["vmid"]).config.get()
            # print(config)
            vm_name = config["name"]
            vm_net_info = config["net0"].lower()
            mac = ""
            for com in vm_net_info.split(","):
                sym = com.split("=")
                if sym[0] == "virtio":
                    mac = sym[1]

            if mac:
                model.get_mac(mac.lower()).add_annotation(f"Attached to virtual machine {vm_name}")
