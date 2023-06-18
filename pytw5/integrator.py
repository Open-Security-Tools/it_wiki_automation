from . import twserver
from . import sources
from . import model
from .config import singleton
from typing import Dict, List
import datetime
import re


class Integrator:
    TAG = "PyTw5Generated"
    RE_LINK = re.compile('\[\[(?P<link>.*?)\]\]')


    def __init__(self):
        now = datetime.datetime.utcnow().strftime("%Y%m%d%H%M%S%f")
        # Trim to milliseconds
        self._now = now[:len("YYYYMMDDHHMMSSMMM")]
        self._model = sources.load_model()

        self._server = twserver.Server.connect(
            url=singleton.twserver_host, 
            user=singleton.twserver_user, 
            password=singleton.twserver_password
        )

    @classmethod
    def _decode_list(cls, value: str) -> List[str]:
        result = []
        matches = list(re.finditer(cls.RE_LINK, value))
        for match in reversed(matches):
            result.append(match.group('link'))
            s = match.start()
            e = match.end()
            value = value[:s] + value[e:]

        result += value.split()

        return result        

    def _find_tiddlers(self, tag: str, twit_class: str) -> Dict[str, str]:
        ret = dict()
        for t in self._server.all_tiddlers:
            if tag in self._decode_list(t.get("tags", "")) and t.get("twit_class") == twit_class:
                ret[t["title"]] = t
        return ret

    def _process_class(self, twit_class: str, target_state: List[Dict[str, str]]) -> None:
        all_tiddler_lookup = {x["title"]: x for x in self._server.all_tiddlers}

        # We identity existing tiddlers using the TAG
        existing_entities = self._find_tiddlers(
            twit_class=twit_class,
            tag=self.TAG,
        )

        # Replace the target state setting the tags and twit_class fields
        old_target_state = target_state
        target_state = dict()
        for item in old_target_state:
            assert "tags" not in item
            assert "twit_class" not in item
            d = dict()
            # Note that TW5 stores field values as strings. So, we need to 
            #      convert them here to ensure we know if they have been changed.
            for k, v in item.items():
                d[k] = str(v)
            d["twit_class"] = twit_class
            target_state[item["title"]] = d

        # Anything in existing which isn't in target state should be deleted.
        to_delete = set(existing_entities.keys()).difference(target_state.keys())
        for title in to_delete:
            # Sanity check...
            self._server.delete_tiddler(title)

        for entity in target_state.values():
            title = entity["title"]
            try:
                existing = all_tiddler_lookup[title]
            except KeyError:
                existing = None
            else:
                # Sanity check...
                if self.TAG not in self._decode_list(existing.get("tags", "")):
                    print(f"WARNING: Unable to update '{title}' - missing tag {self.TAG}")
                    entity = None

                for meta_field in ("revision", "created", "modified", "type", "text", "tags"):
                    if meta_field in existing:
                        del existing[meta_field]
            
            # If we have something to set and either (1) it's new of (2) it is different
            if entity and (existing is None or entity != existing):

                if existing and False:
                    import json
                    print("DEBUG UPDATING...")
                    print("EXISTING:")
                    print(json.dumps(existing, indent=4))
                    print("NEW")
                    print(json.dumps(entity, indent=4))


                tiddler = dict()
                tiddler.update(entity)
                tiddler["revision"] = 0
                tiddler["created"] = self._now
                tiddler["modified"] = self._now
                tiddler["tags"] = f"[[{self.TAG}]]"

                try:
                    tiddler["revision"] = int(existing_entities[title]["revision"]) + 1
                except KeyError:
                    pass
                try:
                    tiddler["created"] = existing_entities[title]["created"]
                except KeyError:
                    pass
                self._server.update_tiddler(tiddler)

    def process_network_interfaces(self) -> None:
        target_state = list()

        for mac in self._model.mac_addresses:
            target_state.append({
                "title": mac.mac,
                "mac": mac.mac,
                "ip_addresses": self._encode_list([x.ipv4 for x in mac.ip_addresses]),
                "annotations": self._encode_list(mac.annotations),
            })

        self._process_class(twit_class="nic", target_state=target_state)

    def process_ip_addresses(self) -> None:
        target_state = list()

        for ip_address in self._model.ip_addresses:
            target_state.append({
                "title": ip_address.ipv4,
                "annotations": self._encode_list(ip_address.annotations),
                "ip_address": ip_address.ipv4,
                "mac": ip_address.mac.mac if ip_address.mac else "",
                "network": ip_address.network.network if ip_address.network else "",
                "hosts": self._encode_list([x.host for x in ip_address.dns_lookups]),
            })

        self._process_class(twit_class="ip_address", target_state=target_state)

    @classmethod
    def _encode_list(cls, value: List[str]) -> str:
        def _del_str(v: str) -> str:
            if " " in v:
                return f"[[{v}]]"
            return v
        return " ".join([_del_str(x) for x in value])

    def process_networks(self) -> None:
        target_state = list()

        for network in self._model.networks:
            target_state.append({
                "title": network.network,
                "network": network.network,
                "vlan": network.vlan or "",  # Note - convert from None to empty string.
                "prefix_length": network.prefix_length,
                "annotations": self._encode_list(network.annotations),
                "ip_addresses": self._encode_list([x.ipv4 for x in network.ip_addresses]),
            })

        self._process_class(twit_class="network", target_state=target_state)

    def process_dns_lookups(self) -> None:
        target_state = list()

        for dns_lookup in self._model.dns_lookups:
            target_state.append({
                "title": dns_lookup.host,
                "host": dns_lookup.host,
                "ip_addresses": self._encode_list([x.ipv4 for x in dns_lookup.ip_addresses]),
                "annotations": self._encode_list(dns_lookup.annotations),
            })

        self._process_class(twit_class="dns_lookup", target_state=target_state)
