import unittest
import pytw5.model


class TestModelImplementation(unittest.TestCase):

    def test_mac_address(self) -> None:
        model = pytw5.model.create_model()
        mac = "aa:12:34:45:56"
        mac_obj = model.get_mac(mac=mac)
        self.assertEqual(mac, mac_obj.mac)
        n = model.get_network("192.168.1.0/24")
        n.add_annotation("test network")
        ipv4 = "192.168.1.4"
        ipv4_obj = model.get_ip_address(ipv4)
        assert ipv4_obj.ipv4 in [x.ipv4 for x in n.ip_addresses]
        d = model.get_dns_lookup("a.b.c")
        d.add_ip_address(ipv4_obj)
        