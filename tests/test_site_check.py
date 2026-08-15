#!/usr/bin/env python3
"""Focused regression tests for the public-site privacy gate."""
import importlib.util
from pathlib import Path
import unittest


CHECK = Path(__file__).with_name("site-check.py")
SPEC = importlib.util.spec_from_file_location("site_check", CHECK)
site_check = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(site_check)


class PrivateIpLiteralTests(unittest.TestCase):
    def test_rejects_private_ipv6_ula_and_link_local_literals(self):
        content = "device addresses: fd12::1 and fe80::1"

        self.assertEqual(
            site_check.private_ip_literals(content),
            ["fd12::1", "fe80::1"],
        )

    def test_keeps_public_ipv6_and_loopback_exemptions(self):
        content = "public 2001:4860:4860::8888 and loopback ::1"

        self.assertEqual(site_check.private_ip_literals(content), [])


if __name__ == "__main__":
    unittest.main()