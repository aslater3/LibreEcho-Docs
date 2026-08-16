#!/usr/bin/env python3
"""Focused regression tests for the public-site privacy gate."""
import importlib.util
from pathlib import Path
import re
import tempfile
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

    def test_rejects_private_ipv4_ranges_beyond_literal_placeholders(self):
        content = "private 10.42.0.5 and 172.31.2.4 and 192.168.44.9"

        self.assertEqual(
            site_check.private_ip_literals(content),
            ["10.42.0.5", "172.31.2.4", "192.168.44.9"],
        )

    def test_rejects_mac_and_local_path_patterns(self):
        self.assertIsNotNone(site_check.MAC_PATTERN.search("aa:bb:cc:dd:ee:ff"))
        self.assertIsNotNone(
            site_check.LOCAL_PATH_PATTERN.search("/home/alice/private/manifest.json")
        )

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

    def test_public_text_scan_includes_extensionless_files(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            license_file = root / "LICENSE"
            license_file.write_text("support endpoint: 10.42.0.5\n", encoding="utf-8")

            files = dict(site_check.public_text_files(root))

        self.assertEqual(site_check.private_ip_literals(files[license_file]), ["10.42.0.5"])


if __name__ == "__main__":
    unittest.main()