#!/usr/bin/env python3
"""Convert blocking main.css and components.css to async preload loading."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

ASYNC_FILES = ("main.css", "components.css")


def async_stylesheet(href: str, indent: str) -> str:
    return (
        f'{indent}<link rel="preload" href="{href}" as="style" '
        f'onload="this.onload=null;this.rel=\'stylesheet\'">\n'
        f'{indent}<noscript><link rel="stylesheet" href="{href}"></noscript>'
    )


def patch_stylesheet(content: str, filename: str) -> str:
    pattern = re.compile(
        rf'(\s*)<link rel="stylesheet" href="((?:\.\./)?assets/css/{re.escape(filename)}(?:\?v=[^"]+)?)">\s*',
        re.MULTILINE,
    )

    def repl(match: re.Match[str]) -> str:
        indent = match.group(1) or "  "
        href = match.group(2)
        return "\n" + async_stylesheet(href, indent) + "\n"

    return pattern.sub(repl, content)


def patch_file(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    orig = text
    changes: list[str] = []
    for name in ASYNC_FILES:
        new_text = patch_stylesheet(text, name)
        if new_text != text:
            changes.append(name)
            text = new_text
    if text != orig:
        path.write_text(text, encoding="utf-8")
    return changes


def main() -> None:
    changed: list[str] = []
    for path in sorted(ROOT.rglob("*.html")):
        if "node_modules" in path.parts:
            continue
        items = patch_file(path)
        if items:
            rel = path.relative_to(ROOT)
            changed.append(f"{rel}: {', '.join(items)}")
    print(f"Updated {len(changed)} files")
    for line in changed:
        print(line)


if __name__ == "__main__":
    main()
