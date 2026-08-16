#!/usr/bin/env python3
"""OCR-based privacy gate for committed GitHub Pages fallback screenshots."""
from __future__ import annotations

import ipaddress
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IMAGES = (
    ROOT / "assets/images/ui-dashboard.png",
    ROOT / "assets/images/ui-system.png",
)

IPV4_PATTERN = re.compile(r"(?<![\d.])(?:\d{1,3}\.){3}\d{1,3}(?![\d.])")
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
    r"(?:LibreEcho[-_]\d{4,}|\b\d{8}T\d{6}Z-[0-9A-Fa-f]{8,}|\b[0-9A-Fa-f]{8}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{4}-[0-9A-Fa-f]{8,})"
)
KERNEL_ID_PATTERN = re.compile(r"\bg\w{7,}-dirty\b")


def private_ips(text: str) -> list[str]:
    values = IPV4_PATTERN.findall(text) + IPV6_PATTERN.findall(text)
    result: list[str] = []
    for value in values:
        if value == "::":
            continue
        try:
            address = ipaddress.ip_address(value)
        except ValueError:
            continue
        if address.is_private and not address.is_loopback:
            result.append(value)
    return result


def ocr(path: Path) -> str:
    try:
        completed = subprocess.run(
            ["tesseract", str(path), "stdout", "--psm", "11"],
            check=True,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError as exc:
        raise RuntimeError("tesseract is required for fallback screenshot validation") from exc
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(f"tesseract failed for {path.name}: {exc.stderr.strip()}") from exc
    return completed.stdout


def main() -> int:
    failures: list[str] = []
    for image in IMAGES:
        if not image.is_file():
            failures.append(f"missing fallback screenshot: {image.relative_to(ROOT)}")
            continue
        text = ocr(image)
        for value in private_ips(text):
            failures.append(f"private IP in {image.name}: {value}")
        if MAC_PATTERN.search(text):
            failures.append(f"MAC address in {image.name}")
        if LOCAL_PATH_PATTERN.search(text):
            failures.append(f"local filesystem path in {image.name}")
        if DEVICE_ID_PATTERN.search(text):
            failures.append(f"device/build identifier in {image.name}")
        if KERNEL_ID_PATTERN.search(text):
            failures.append(f"dirty kernel identifier in {image.name}")

    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1
    print(f"PASS: OCR privacy checks passed for {len(IMAGES)} committed fallback screenshots")
    return 0


if __name__ == "__main__":
    sys.exit(main())
