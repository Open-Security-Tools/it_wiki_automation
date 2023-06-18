import os
import logging
from typing import Any, Dict
import json
from click import ClickException

log = logging.getLogger(__name__)


class MissingConfigError(ClickException):
    pass


class Singleton:

    def __init__(self) -> None:
        self._path = ""
        self._config_loaded = False
        self._lazy_config = dict()  # type: Dict[str, Any]

    def initialise(self, p: str) -> None:
        self._path = os.path.abspath(os.path.expanduser(p))
        self._config_loaded = False
        self._lazy_config.clear()
        log.debug("Path: '{}'".format(self._path))

    @property
    def path(self) -> str:
        return self._path

    @property
    def server_config_path(self) -> str:
        return os.path.join(self._path, "pytw5.config")

    @property
    def _config(self) -> Dict[str, Any]:

        if not self._config_loaded:
            try:
                with open(self.server_config_path, "r") as fp:
                    self._lazy_config = json.load(fp=fp)
            except FileNotFoundError:
                raise MissingConfigError("Missing config '{}'".format(self.server_config_path))
            except json.decoder.JSONDecodeError as e:
                raise ClickException(f"Json parsing error ({str(e)})!") from None
            self._config_loaded = True
        return self._lazy_config

    def _get_key(self, key: str) -> str:
        try:
            return self._config[key]
        except KeyError:
            raise ClickException(f"Missing '{key}' configuration key!") from None

    # TiddlyWiki Server containing TWIT

    @property
    def twserver_host(self) -> str:
        return self._get_key("twserver_host")

    @property
    def twserver_user(self) -> str:
        return self._get_key("twserver_user")

    @property
    def twserver_password(self) -> str:
        return self._get_key("twserver_password")

    # PFSense

    @property
    def pfsense_host(self) -> str:
        return self._get_key("pfsense_host")

    @property
    def pfsense_client_id(self) -> str:
        return self._get_key("pfsense_client_id")

    @property
    def pfsense_token(self) -> str:
        return self._get_key("pfsense_token")

    # Proxmox

    @property
    def proxmox_user(self) -> str:
        return self._get_key("proxmox_user")

    @property
    def proxmox_password(self) -> str:
        return self._get_key("proxmox_password")

    @property
    def proxmox_host(self) -> str:
        return self._get_key("proxmox_host")

    # Unifi

    @property
    def unifi_controller_ip(self) -> str:
        return self._get_key("unifi_controller_ip")

    @property
    def unifi_user(self) -> str:
        return self._get_key("unifi_user")

    @property
    def unifi_password(self) -> str:
        return self._get_key("unifi_password")



singleton = Singleton()
