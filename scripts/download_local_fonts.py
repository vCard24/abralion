#!/usr/bin/env python3
"""Download Inter + Montserrat woff2 (latin + latin-ext for Turkish)."""
from __future__ import annotations

import hashlib
import re
import ssl
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FONT_DIR = ROOT / "assets" / "fonts"
CSS_OUT = ROOT / "assets" / "css" / "fonts.css"

GOOGLE_CSS = (
    "https://fonts.googleapis.com/css2?"
    "family=Inter:wght@400;500;700&family=Montserrat:wght@600;700&display=swap"
)

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)


def fetch_google_css() -> str:
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    req = urllib.request.Request(GOOGLE_CSS, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60, context=ctx) as resp:
        return resp.read().decode("utf-8")


def subset_label(unicode_range: str) -> str | None:
    if "U+0000-00FF" in unicode_range:
        return "latin"
    if "U+0100-02BA" in unicode_range or "U+0100-024F" in unicode_range:
        return "latin-ext"
    return None


def slug_from_block(block: str) -> tuple[str, str] | None:
    family_m = re.search(r"font-family:\s*['\"]?([^;'\"]+)", block)
    weight_m = re.search(r"font-weight:\s*(\d+)", block)
    range_m = re.search(r"unicode-range:\s*([^;]+)", block)
    if not family_m or not weight_m or not range_m:
        return None
    label = subset_label(range_m.group(1))
    if not label:
        return None
    name = family_m.group(1).strip().replace(" ", "-").lower()
    return f"{name}-{label}-{weight_m.group(1)}-normal.woff2", range_m.group(1).strip()


def main() -> None:
    FONT_DIR.mkdir(parents=True, exist_ok=True)
    for old in FONT_DIR.glob("*.woff2"):
        old.unlink()

    css = fetch_google_css()
    blocks = re.findall(r"@font-face\s*\{[^}]+\}", css, flags=re.I | re.S)

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    local_faces: list[str] = []

    for block in blocks:
        url_m = re.search(r"url\((https://[^)]+woff2)\)", block)
        if not url_m:
            continue
        parsed = slug_from_block(block)
        if not parsed:
            continue
        filename, unicode_range = parsed
        url = url_m.group(1)

        dest = FONT_DIR / filename
        if not dest.is_file():
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=60, context=ctx) as resp:
                dest.write_bytes(resp.read())
            print(f"Wrote {dest.relative_to(ROOT)} ({dest.stat().st_size} bytes)")

        family_m = re.search(r"font-family:\s*['\"]?([^;'\"]+)", block)
        weight_m = re.search(r"font-weight:\s*(\d+)", block)
        family = family_m.group(1).strip() if family_m else "Inter"
        weight = weight_m.group(1) if weight_m else "400"

        local_faces.append(
            f"@font-face {{\n"
            f"  font-family: '{family}';\n"
            f"  font-style: normal;\n"
            f"  font-weight: {weight};\n"
            f"  font-display: optional;\n"
            f"  src: url('../fonts/{filename}') format('woff2');\n"
            f"  unicode-range: {unicode_range};\n"
            f"}}"
        )

    if not local_faces:
        raise SystemExit("No latin/latin-ext font faces downloaded")

    CSS_OUT.write_text(
        "/* Self-hosted Inter + Montserrat (latin + latin-ext). font-display: optional */\n\n"
        + "\n\n".join(local_faces)
        + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {CSS_OUT.relative_to(ROOT)} ({len(local_faces)} faces)")


if __name__ == "__main__":
    main()
