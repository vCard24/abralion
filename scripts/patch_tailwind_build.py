#!/usr/bin/env python3
"""Replace Tailwind CDN with built assets/css/tailwind.css in HTML files."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TAILWIND_VER = "20260702"

CDN_BLOCK = re.compile(
    r'\s*<script src="https://cdn\.tailwindcss\.com(?:\?plugins=forms)?"></script>\s*'
    r'(?:<script src="(\.\./)?assets/js/tailwind-config\.js"></script>\s*)?',
    re.MULTILINE,
)

TAILWIND_LINK = re.compile(
    r'\s*<link rel="stylesheet" href="(\.\./)?assets/css/tailwind\.css(?:\?v=[^"]+)?">\s*',
    re.MULTILINE,
)


def patch(content: str, prefix: str) -> str:
    link = (
        f'  <link rel="stylesheet" href="{prefix}assets/css/tailwind.css?v={TAILWIND_VER}">\n'
    )
    content = CDN_BLOCK.sub("\n", content)
    content = re.sub(
        r'\s*<script src="(\.\./)?assets/js/tailwind-config\.js"></script>\s*',
        "\n",
        content,
    )
    if TAILWIND_LINK.search(content):
        content = TAILWIND_LINK.sub("\n" + link, content, count=1)
    else:
        content = re.sub(
            r'(<link rel="stylesheet" href="' + re.escape(prefix) + r'assets/css/main\.css">)',
            link + r"\1",
            content,
            count=1,
        )
    return content


def main() -> None:
    changed: list[str] = []
    for path in sorted(ROOT.rglob("*.html")):
        if "node_modules" in path.parts:
            continue
        prefix = "../" if path.parent.name == "urun" else ""
        text = path.read_text(encoding="utf-8")
        new_text = patch(text, prefix)
        if new_text != text:
            path.write_text(new_text, encoding="utf-8")
            changed.append(str(path.relative_to(ROOT)))
    print(f"Updated {len(changed)} files")
    for name in changed:
        print(name)


if __name__ == "__main__":
    main()
