#!/usr/bin/env python3
"""Static contract checks for the public LibreEcho website."""
from html.parser import HTMLParser
import ipaddress
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"
CSS = ROOT / "assets/css/site.css"
ROADMAP_CSS = ROOT / "assets/css/roadmap.css"
SCRIPT = ROOT / "assets/js/site.js"
PAGES_WORKFLOW = ROOT / ".github/workflows/pages.yml"

REQUIRED_IDS = {
    "hardware-roadmap",
    "top", "progress", "features", "hardware", "install", "demo",
    "privacy", "releases", "security", "licensing", "tester", "contribute",
}
REQUIRED_TEXT = [
    "Stable release 0.13.10 available",
    "Open Beta has not launched",
    "LibreEcho radar-puffin v0.13.10",
    "Installation is available for supported hardware",
    "0.13.10 Echo 2nd Gen one-shot installation guide",
    "One platform today. More hardware next.",
    "Research candidate",
    "MT8183/Amazon LK groundwork",
    "Suggested porting priority",
    "physical mute is not a beta-supported privacy guarantee",
    "browser-local simulation",
]
FORBIDDEN_TEXT = [
    'href="https://github.com/"',
    "/home/andy/",
    "192.168.",
    "10.0.",
    "172.16.",
    "G2A0RF",
]

class SiteParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.links = []
        self.assets = []
        self.text = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get("id"):
            self.ids.add(attrs["id"])
        if tag == "a" and attrs.get("href"):
            self.links.append(attrs["href"])
        if tag in {"img", "script", "link"}:
            value = attrs.get("src") or attrs.get("href")
            if value:
                self.assets.append(value)

    def handle_data(self, data):
        self.text.append(data)


def fail(message):
    print(f"FAIL: {message}")
    return 1


IPV4_PATTERN = re.compile(r"(?<![\d.])(?:\d{1,3}\.){3}\d{1,3}(?![\d.])")
# Keep this deliberately broad, then let ipaddress validate candidates.  This
# catches compressed values such as fd12::1 and fe80::1 without treating CSS
# hex colours, MAC addresses, or other colon-separated strings as addresses.
IPV6_PATTERN = re.compile(
    r"(?<![0-9A-Fa-f:])(?:[0-9A-Fa-f]{0,4}:){2,7}[0-9A-Fa-f]{0,4}(?![0-9A-Fa-f:])"
)
MAC_PATTERN = re.compile(
    r"(?<![0-9A-Fa-f])(?:[0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}(?![0-9A-Fa-f])"
)
LOCAL_PATH_PATTERN = re.compile(
    r"(?:/home/[^/\s]+(?:/[^\s]*)?|/Users/[^/\s]+(?:/[^\s]*)?|[A-Za-z]:\\Users\\[^\s]+)"
)
DEVICE_ID_PATTERN = re.compile(
    r"(?:LibreEcho[-_]\d{4,}|\b\d{8}T\d{6}Z-[0-9A-Fa-f]{8,}|\b[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{12})"
)
KERNEL_ID_PATTERN = re.compile(r"\bg\w{7,}-dirty\b")


def private_ip_literals(content):
    """Return non-loopback private IP literals embedded in *content*."""
    values = list(IPV4_PATTERN.findall(content)) + list(IPV6_PATTERN.findall(content))
    private = []
    for value in values:
        # A bare double colon is also the CSS pseudo-element selector.
        if value == "::":
            continue
        try:
            address = ipaddress.ip_address(value)
        except ValueError:
            continue
        if address.is_private and not address.is_loopback:
            private.append(value)
    return private


def public_text_files(root, excluded=None):
    """Return UTF-8 text files that will be copied into the Pages artifact."""
    excluded = set(excluded or ())
    for path in root.rglob("*"):
        if not path.is_file() or path in excluded:
            continue
        if ".git" in path.parts or ".github" in path.parts or "tests" in path.parts or "ui-source" in path.parts:
            continue
        try:
            yield path, path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue


def main():
    source = INDEX.read_text(encoding="utf-8")
    css = CSS.read_text(encoding="utf-8")
    roadmap_css = ROADMAP_CSS.read_text(encoding="utf-8")
    script = SCRIPT.read_text(encoding="utf-8")
    pages_workflow = PAGES_WORKFLOW.read_text(encoding="utf-8")
    parser = SiteParser()
    parser.feed(source)
    errors = []

    missing = REQUIRED_IDS - parser.ids
    if missing:
        errors.append(f"missing section ids: {', '.join(sorted(missing))}")

    text = " ".join(parser.text)
    for needle in REQUIRED_TEXT:
        if needle not in text:
            errors.append(f"missing required copy: {needle}")
    public_text = {INDEX: source}
    for path, content in public_text_files(ROOT, excluded={INDEX, Path(__file__)}):
        public_text[path] = content

    for path, content in public_text.items():
        for needle in FORBIDDEN_TEXT:
            if needle in content:
                errors.append(f"forbidden/private placeholder present in {path.relative_to(ROOT)}: {needle}")
        for value in private_ip_literals(content):
            address = ipaddress.ip_address(value)
            family = "IPv6" if address.version == 6 else "IPv4"
            errors.append(f"private {family} address present in {path.relative_to(ROOT)}: {value}")
        if MAC_PATTERN.search(content):
            errors.append(f"MAC address present in {path.relative_to(ROOT)}")
        if LOCAL_PATH_PATTERN.search(content):
            errors.append(f"local filesystem path present in {path.relative_to(ROOT)}")
        if DEVICE_ID_PATTERN.search(content):
            errors.append(f"device/build identifier present in {path.relative_to(ROOT)}")
        if KERNEL_ID_PATTERN.search(content):
            errors.append(f"dirty kernel identifier present in {path.relative_to(ROOT)}")

    for href in parser.links:
        if href.startswith("#"):
            if href[1:] and href[1:] not in parser.ids:
                errors.append(f"broken in-page link: {href}")
        elif href.startswith(("assets/", "./")):
            if not (ROOT / href.removeprefix("./")).is_file():
                errors.append(f"missing linked local asset: {href}")

    for asset in parser.assets:
        if asset.startswith(("assets/", "./")) and not (ROOT / asset.removeprefix("./")).is_file():
            errors.append(f"missing document asset: {asset}")

    if not re.search(r'<time datetime="2026-09-04">4 September 2026</time>', source):
        errors.append("maintained review date is missing or inconsistent")

    release_tag = "radar-puffin-v0.13.10"
    release_base = f"https://github.com/aslater3/LibreEcho/releases/download/{release_tag}"
    release_assets = [
        "libreecho-radar-puffin-v0.13.10-initial-install.tar",
        "libreecho-radar-puffin-v0.13.10-run-one-shot.sh",
        "libreecho-radar-puffin-v0.13.10.ota.tar",
        "libreecho-radar-puffin-v0.13.10-SHA256SUMS",
        "libreecho-radar-puffin-v0.13.10-ota-public-key.hex",
        "libreecho-radar-puffin-v0.13.10-release-notes.md",
    ]
    for asset in release_assets:
        immutable_href = f"{release_base}/{asset}"
        if immutable_href not in parser.links:
            errors.append(f"release asset is not linked for {release_tag}: {asset}")
        moving_href = f"https://github.com/aslater3/LibreEcho/releases/latest/download/{asset}"
        if moving_href in parser.links:
            errors.append(f"release asset uses moving latest tag: {asset}")

    install_guide = f"https://github.com/aslater3/LibreEcho/blob/{release_tag}/docs/install/README.md"
    if install_guide not in parser.links:
        errors.append("installation guide is not pinned to the current stable release")
    if f"https://github.com/aslater3/LibreEcho/releases/tag/{release_tag}" not in parser.links:
        errors.append("current stable release page is not linked")

    if 'href="#security">Support</a>' not in source:
        errors.append("header Support link must route to support guidance")

    if "<details class=\"roadmap-disclosure\">" not in source or "Show the full hardware compatibility matrix" not in source:
        errors.append("hardware roadmap matrix must be collapsed behind an accessible details disclosure")
    if "@media(max-width:1400px){.primary-nav" not in css:
        errors.append("header collapse breakpoint must accommodate the roadmap navigation link")
    if ".status-research" not in roadmap_css:
        errors.append("research-candidate status needs a distinct visual treatment")
    if '<html lang="en-GB" class="no-js">' not in source:
        errors.append("document does not provide the no-js progressive-enhancement marker")
    if 'document.documentElement.classList.replace("no-js", "js");' not in script:
        errors.append("site script does not enable the JavaScript navigation state")
    if ".primary-nav{display:flex;" not in css or ".js .primary-nav{display:none}" not in css:
        errors.append("mobile navigation is not visible by default before JavaScript enhancement")
    if ".js .menu-toggle{display:block;" not in css:
        errors.append("mobile menu toggle is not limited to the JavaScript-enhanced state")
    docs_css = (ROOT / "assets/css/docs.css").read_text(encoding="utf-8")
    if ".button-secondary" not in docs_css or "color:var(--text)!important" not in docs_css:
        errors.append("secondary CTA must override the base button text colour")
    if "--exclude='tests'" not in pages_workflow or "--exclude='.github'" not in pages_workflow:
        errors.append("Pages artifact must exclude repository tests and workflow sources")
    if "max-height:calc(100vh - 4.5rem)" not in css or "overflow-y:auto" not in css:
        errors.append("no-JavaScript mobile navigation must scroll within the viewport")
    if ".hero-actions,.contribute-links{display:flex;align-items:center;gap:1.4rem;margin-top:2rem;flex-wrap:wrap}" not in css:
        errors.append("desktop hero actions must wrap within the capped copy column")

    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    print(f"PASS: {INDEX} has {len(parser.ids)} ids, {len(parser.links)} links, and {len(parser.assets)} local asset references")
    return 0


if __name__ == "__main__":
    sys.exit(main())
