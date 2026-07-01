#!/usr/bin/env python3
"""Apply non-blocking CSS/font loading and drop compare.css where unused."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

ASYNC_CSS = (
    "responsive.css",
    "dark-theme.css",
    "site-extra.css",
    "noir-migration.css",
)

COMPARE_PAGES = {"karsilastir.html"}

THEME_INLINE = (
    '<script>document.documentElement.classList.add("dark-theme","dark");</script>\n'
)

FONTS_TEXT = (
    "https://fonts.googleapis.com/css2?"
    "family=Inter:wght@400;500;700"
    "&family=JetBrains+Mono:wght@500"
    "&family=Montserrat:wght@600;700"
    "&display=swap"
)
FONTS_ICONS = (
    "https://fonts.googleapis.com/css2?"
    "family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@24,400,0,0"
    "&display=swap"
)


def async_stylesheet(href: str) -> str:
    return (
        f'  <link rel="preload" href="{href}" as="style" '
        f'onload="this.onload=null;this.rel=\'stylesheet\'">\n'
        f'  <noscript><link rel="stylesheet" href="{href}"></noscript>'
    )


def patch_fonts(content: str) -> str:
    old = re.compile(
        r'\s*<link rel="preconnect" href="https://fonts\.googleapis\.com">\s*'
        r'<link rel="preconnect" href="https://fonts\.gstatic\.com" crossorigin>\s*'
        r'<link href="https://fonts\.googleapis\.com/css2\?[^"]+" rel="stylesheet">\s*',
        re.MULTILINE,
    )
    if not old.search(content):
        return content
    block = (
        '  <link rel="preconnect" href="https://fonts.googleapis.com">\n'
        '  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
        + async_stylesheet(FONTS_TEXT)
        + "\n"
        + async_stylesheet(FONTS_ICONS)
        + "\n"
    )
    return old.sub("\n" + block, content, count=1)


def patch_blocking_css(content: str, prefix: str) -> str:
    for name in ASYNC_CSS:
        pattern = re.compile(
            rf'\s*<link rel="stylesheet" href="{re.escape(prefix)}assets/css/{re.escape(name)}(?:\?v=[^"]+)?">\s*',
            re.MULTILINE,
        )
        href = f"{prefix}assets/css/{name}"
        if name != "dark-theme.css":
            href += "?v=20260603" if "?" not in name else ""
        if name == "dark-theme.css":
            href = f"{prefix}assets/css/dark-theme.css"
        content = pattern.sub("\n" + async_stylesheet(href) + "\n", content, count=1)
    return content


def patch_theme_init(content: str) -> str:
    if THEME_INLINE.strip() in content:
        return content
    content = content.replace(
        '<body',
        THEME_INLINE + "  <body",
        1,
    )
    content = re.sub(
        r'\s*<script src="(\.\./)?assets/js/theme-init\.js"></script>\s*',
        "\n",
        content,
        count=1,
    )
    return content


def patch_compare_css(content: str, rel_path: str) -> str:
    if rel_path.replace("\\", "/") in COMPARE_PAGES:
        return content
    return re.sub(
        r'\s*<link rel="stylesheet" href="(\.\./)?assets/css/compare\.css(?:\?v=[^"]+)?">\s*',
        "\n",
        content,
    )


def patch_file(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    orig = text
    rel = str(path.relative_to(ROOT)).replace("\\", "/")
    prefix = "../" if path.parent.name == "urun" else ""

    text = patch_fonts(text)
    text = patch_blocking_css(text, prefix)
    text = patch_theme_init(text)
    text = patch_compare_css(text, rel)

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
    print(f"Updated {len(changed)} files")
    for name in changed:
        print(name)


if __name__ == "__main__":
    main()
