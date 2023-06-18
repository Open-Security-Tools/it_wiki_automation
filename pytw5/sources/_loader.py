from .. model import Model, create_model
from . import pfsense
from . import proxmox
from . import unifi


def load_model() -> Model:
    m = create_model()

    pfsense.load_model(m)
    proxmox.load_model(m)
    unifi.load_model(m)

    return m
