#!/usr/bin/env python3
"""Focused regression coverage for the responsive primary navigation."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
CSS = (ROOT / "assets/css/site.css").read_text(encoding="utf-8")


class HeaderResponsiveTests(unittest.TestCase):
    def test_collapses_before_capped_container_overflow_range(self):
        match = re.search(r"@media\(max-width:(\d+)px\)\{\.primary-nav", CSS)
        if match is None:
            self.fail("header collapse media query is missing")
        breakpoint = int(match.group(1))
        # The 14-item header (including the donation button and roadmap link)
        # needs the wider breakpoint to avoid intrinsic-width overflow.
        self.assertGreaterEqual(breakpoint, 1400)
        self.assertLessEqual(breakpoint, 1400)

    def test_expanded_header_uses_compact_intrinsic_sizing(self):
        self.assertIn(".primary-nav{display:flex;align-items:center;gap:1rem}", CSS)
        self.assertIn(
            ".primary-nav>a{color:var(--muted);text-decoration:none;font-size:.88rem;white-space:nowrap}",
            CSS,
        )
        self.assertIn(".primary-nav .button{white-space:nowrap;flex-shrink:0}", CSS)


if __name__ == "__main__":
    unittest.main()
