#!/usr/bin/env python3
"""Focused regression tests for the public-site privacy gate."""
import importlib.util
from pathlib import Path
import re
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

    def test_rendered_ui_gate_rejects_ipv6_ula_and_link_local_values(self):
        workflow = (site_check.ROOT / ".github/workflows/pages.yml").read_text(
            encoding="utf-8"
        )

        self.assertIn("f[cd][0-9a-f]{2}:", workflow)
        self.assertIn("fe[89ab][0-9a-f]:", workflow)
        self.assertRegex(workflow, r"privateData = /[^/]+f\[cd\]\[0-9a-f\]\{2\}:")

        rendered_ipv6 = re.compile(
            r"(?:f[cd][0-9a-f]{2}:|fe[89ab][0-9a-f]:)[0-9a-f:]*", re.IGNORECASE
        )
        for value in ("fd12::1", "FE80::1"):
            self.assertIsNotNone(rendered_ipv6.search(value), value)


if __name__ == "__main__":
    unittest.main()