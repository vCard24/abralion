#!/usr/bin/env python3
"""Stage 1: permanent dark theme classes + single CSS bundle link."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BUNDLE_VERSION = "20260523"

BUNDLE_FILES = (
    "tailwind.css",
    "noir-migration.css",
    "dark-theme.css",
    "main.css",
    "components.css",
    "responsive.css",
    "site-extra.css",
)

THEME_SCRIPT = re.compile(
    r'\s*<script>document\.documentElement\.classList\.add\("dark-theme"(?:,"dark")?\)'
    r'(?:;document\.body\.classList\.add\("dark-theme"\))?;</script>\s*',
    re.MULTILINE,
)

INDEX_NOSCRIPT_BUNDLE = re.compile(
    r"\s*<noscript>\s*"
    r'(?:<link rel="stylesheet" href="assets/css/(?:tailwind|noir-migration|dark-theme)\.css[^"]*">\s*)+'
    r"</noscript>\s*",
    re.MULTILINE,
)


def css_href_pattern(prefix: str, filename: str) -> str:
    return re.escape(f"{prefix}assets/css/{filename}")


def remove_bundle_css_links(content: str, prefix: str) -> str:
    for name in BUNDLE_FILES:
        href = css_href_pattern(prefix, name)
        content = re.sub(
            rf'\s*<link rel="stylesheet" href="{href}(?:\?v=[^"]*)?"[^>]*>\s*',
            "\n",
            content,
        )
        content = re.sub(
            rf'\s*<link rel="preload" href="{href}(?:\?v=[^"]*)?" as="style"[^>]*>\s*',
            "\n",
            content,
        )
        content = re.sub(
            rf'\s*<noscript><link rel="stylesheet" href="{href}(?:\?v=[^"]*)?"></noscript>\s*',
            "\n",
            content,
        )
    content = INDEX_NOSCRIPT_BUNDLE.sub("\n", content)
    return content


def ensure_bundle_link(content: str, prefix: str) -> str:
    bundle_href = f'{prefix}assets/css/bundle.min.css?v={BUNDLE_VERSION}'
    if bundle_href in content:
        return content
    bundle_tag = f'  <link rel="stylesheet" href="{bundle_href}">\n'
    if '<link rel="icon"' in content:
        return content.replace("<link rel=\"icon\"", bundle_tag + "  <link rel=\"icon\"", 1)
    return re.sub(r"(</head>)", bundle_tag + r"\1", content, count=1)


def patch_html_element(content: str) -> str:
    if re.search(r'<html[^>]*class="[^"]*\bdark-theme\b', content):
        return content
    return re.sub(
        r"<html(\s+lang=\"tr\")(?![^>]*\bclass=)",
        r'<html\1 class="dark-theme dark"',
        content,
        count=1,
    )


def patch_body_class(content: str) -> str:
    def repl(match: re.Match[str]) -> str:
        classes = match.group(1)
        if "dark-theme" in classes.split():
            return match.group(0)
        return f'<body class="{classes} dark-theme"'

    return re.sub(r'<body class="([^"]*)"', repl, content, count=1)


def asset_prefix(path: Path) -> str:
    rel = path.relative_to(ROOT).as_posix()
    if rel.startswith("urun/") or rel.startswith("scripts/templates/"):
        return "../"
    return ""


def cleanup_empty_noscript(content: str) -> str:
    return re.sub(r"\s*<noscript>\s*</noscript>\s*", "\n", content)


def patch_file(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    orig = text
    prefix = asset_prefix(path)

    text = THEME_SCRIPT.sub("\n", text)
    text = patch_html_element(text)
    text = patch_body_class(text)
    text = remove_bundle_css_links(text, prefix)
    text = ensure_bundle_link(text, prefix)
    text = cleanup_empty_noscript(text)
    text = re.sub(r"\n{3,}", "\n\n", text)

    if text != orig:
        path.write_text(text, encoding="utf-8")
        return True
    return False


def main() -> None:
    changed: list[str] = []
    for path in sorted(ROOT.rglob("*.html")):
        if "node_modules" in path.parts:
            continue
        if patch_file(path):
            changed.append(str(path.relative_to(ROOT)))
    print(f"Updated {len(changed)} HTML files")
    for name in changed:
        print(name)


if __name__ == "__main__":
    main()
