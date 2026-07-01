#!/usr/bin/env python3
"""Normalize footer-cert indentation after patch_lighthouse_fixes.py."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

BAD_BLOCK = re.compile(
    r"</p>\n"
    r'<div class="footer-cert" role="group" aria-label="Sertifikasyon işaretleri">\n'
    r'  <img src="((?:\.\./)?assets/images/mpa-logo\.svg)" alt="MPA Hannover" width="82" height="29" loading="lazy" decoding="async">\n'
    r'  <img src="((?:\.\./)?assets/images/eac-logo\.svg)" alt="EAC uygunluk işareti" width="29" height="29" loading="lazy" decoding="async">\n'
    r"</div>\n\n\n",
    re.MULTILINE,
)


def good_block(prefix: str) -> str:
    return (
        "</p>\n"
        "        <div class=\"footer-cert\" role=\"group\" aria-label=\"Sertifikasyon işaretleri\">\n"
        f'          <img src="{prefix}assets/images/mpa-logo.svg" alt="MPA Hannover" '
        'width="82" height="29" loading="lazy" decoding="async">\n'
        f'          <img src="{prefix}assets/images/eac-logo.svg" alt="EAC uygunluk işareti" '
        'width="29" height="29" loading="lazy" decoding="async">\n'
        "        </div>\n"
    )


def main() -> None:
    changed = 0
    for path in sorted(ROOT.rglob("*.html")):
        if "node_modules" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        if 'class="footer-cert"' not in text:
            continue
        prefix = "../" if path.parent.name == "urun" else ""
        new_text, n = BAD_BLOCK.subn(good_block(prefix), text, count=1)
        if n:
            path.write_text(new_text, encoding="utf-8")
            changed += 1
            print(path.relative_to(ROOT))
    print(f"Fixed {changed} files")


if __name__ == "__main__":
    main()
