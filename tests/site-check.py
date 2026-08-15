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
SCRIPT = ROOT / "assets/js/site.js"

REQUIRED_IDS = {
    "top", "progress", "features", "hardware", "install", "demo",
    "privacy", "releases", "security", "licensing", "tester", "contribute",
}
REQUIRED_TEXT = [
    "Developer Preview preparation",
    "Open Beta has not launched",
    "LibreEcho radar-puffin v0.1.0",
    "libreecho-radar-puffin-v0.1.0-SHA256SUMS",
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


def main():
    source = INDEX.read_text(encoding="utf-8")
    css = CSS.read_text(encoding="utf-8")
    script = SCRIPT.read_text(encoding="utf-8")
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
    text_suffixes = {".html", ".css", ".js", ".json", ".md", ".svg", ".xml", ".txt", ".yml", ".yaml"}
    for path in ROOT.rglob("*"):
        if not path.is_file() or path == Path(__file__) or path.suffix.lower() not in text_suffixes:
            continue
        if ".git" in path.parts or "tests" in path.parts or "ui-source" in path.parts:
            continue
        try:
            public_text[path] = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue

    mac_pattern = re.compile(r"(?<![0-9A-Fa-f])(?:[0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}(?![0-9A-Fa-f])")
    for path, content in public_text.items():
        for needle in FORBIDDEN_TEXT:
            if needle in content:
                errors.append(f"forbidden/private placeholder present in {path.relative_to(ROOT)}: {needle}")
        for value in re.findall(r"(?<![\d.])(?:\d{1,3}\.){3}\d{1,3}(?![\d.])", content):
            try:
                address = ipaddress.ip_address(value)
            except ValueError:
                continue
            if address.is_private and not address.is_loopback:
                errors.append(f"private IPv4 address present in {path.relative_to(ROOT)}: {value}")
        if mac_pattern.search(content):
            errors.append(f"MAC address present in {path.relative_to(ROOT)}")

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

    for expected in [
        "libreecho-radar-puffin-v0.1.0-boot.img",
        "libreecho-radar-puffin-v0.1.0.ota.tar",
        "libreecho-radar-puffin-v0.1.0-SHA256SUMS",
        "libreecho-radar-puffin-v0.1.0-ota-public-key.hex",
    ]:
        if expected not in source:
            errors.append(f"release inventory omits {expected}")

    if not re.search(r'<time datetime="2026-08-15">15 August 2026</time>', source):
        errors.append("maintained review date is missing or inconsistent")

    # Mobile navigation must remain reachable when JavaScript is unavailable.
    if '<html lang="en-GB" class="no-js">' not in source:
        errors.append("document does not provide the no-js progressive-enhancement marker")
    if 'document.documentElement.classList.replace("no-js", "js");' not in script:
        errors.append("site script does not enable the JavaScript navigation state")
    if ".primary-nav{display:flex;" not in css or ".js .primary-nav{display:none}" not in css:
        errors.append("mobile navigation is not visible by default before JavaScript enhancement")
    if ".js .menu-toggle{display:block;" not in css:
        errors.append("mobile menu toggle is not limited to the JavaScript-enhanced state")

    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    print(f"PASS: {INDEX} has {len(parser.ids)} ids, {len(parser.links)} links, and {len(parser.assets)} local asset references")
    return 0


if __name__ == "__main__":
    sys.exit(main())
