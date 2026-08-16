#!/usr/bin/env python3
"""OCR-based privacy gate for committed GitHub Pages fallback screenshots."""
from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECK = ROOT / "tests/site-check.py"
SPEC = importlib.util.spec_from_file_location("site_check", CHECK)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("unable to load the shared site privacy checker")
site_check = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(site_check)

IMAGES = (
    ROOT / "assets/images/ui-dashboard.png",
    ROOT / "assets/images/ui-system.png",
)


def private_ips(text: str) -> list[str]:
    return site_check.private_ip_literals(text)


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
        if site_check.MAC_PATTERN.search(text):
            failures.append(f"MAC address in {image.name}")
        if site_check.LOCAL_PATH_PATTERN.search(text):
            failures.append(f"local filesystem path in {image.name}")
        if site_check.DEVICE_ID_PATTERN.search(text):
            failures.append(f"device/build identifier in {image.name}")
        if site_check.KERNEL_ID_PATTERN.search(text):
            failures.append(f"dirty kernel identifier in {image.name}")

    if failures:
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1
    print(f"PASS: OCR privacy checks passed for {len(IMAGES)} committed fallback screenshots")
    return 0


if __name__ == "__main__":
    sys.exit(main())
