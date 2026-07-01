#!/usr/bin/env python3
"""Async noir-migration.css and static footer certification logos."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

FOOTER_BLURB = "Rusya'da faaliyet gösteren EKS-PLAST LLC"


def async_stylesheet(href: str, indent: str = "  ") -> str:
    return (
        f'{indent}<link rel="preload" href="{href}" as="style" '
        f'onload="this.onload=null;this.rel=\'stylesheet\'">\n'
        f'{indent}<noscript><link rel="stylesheet" href="{href}"></noscript>'
    )


def patch_noir_migration(content: str) -> str:
    pattern = re.compile(
        r'(\s*)<link rel="stylesheet" href="((?:\.\./)?assets/css/noir-migration\.css(?:\?v=[^"]+)?)">\s*',
        re.MULTILINE,
    )

    def repl(match: re.Match[str]) -> str:
        indent = match.group(1) or "  "
        href = match.group(2)
        return "\n" + async_stylesheet(href, indent) + "\n"

    return pattern.sub(repl, content)


def footer_cert_block(prefix: str, indent: str) -> str:
    return (
        f'{indent}<div class="footer-cert" role="group" aria-label="Sertifikasyon işaretleri">\n'
        f'{indent}  <img src="{prefix}assets/images/mpa-logo.svg" alt="MPA Hannover" '
        f'width="82" height="29" loading="lazy" decoding="async">\n'
        f'{indent}  <img src="{prefix}assets/images/eac-logo.svg" alt="EAC uygunluk işareti" '
        f'width="29" height="29" loading="lazy" decoding="async">\n'
        f"{indent}</div>"
    )


def patch_footer_certs(content: str, prefix: str) -> str:
    if 'class="footer-cert"' in content:
        return content
    if FOOTER_BLURB not in content or "<footer" not in content:
        return content

    marker = re.compile(
        r'(<footer\b[\s\S]*?<div class="space-y-6">\s*'
        r'<a[^>]*footer-logo-link[^>]*>[\s\S]*?</a>\s*'
        r'(\s*)(<p[^>]*>[\s\S]*?'
        + re.escape(FOOTER_BLURB)
        + r"[\s\S]*?</p>)\s*)",
        re.MULTILINE,
    )
    match = marker.search(content)
    if not match:
        return content

    indent = match.group(2) or "        "
    insert = footer_cert_block(prefix, indent) + "\n"
    return content[: match.end(3)] + "\n" + insert + content[match.end(3) :]


def patch_file(path: Path) -> tuple[bool, list[str]]:
    text = path.read_text(encoding="utf-8")
    orig = text
    changes: list[str] = []
    prefix = "../" if path.parent.name == "urun" else ""

    new_text = patch_noir_migration(text)
    if new_text != text:
        changes.append("noir-migration async")
        text = new_text

    new_text = patch_footer_certs(text, prefix)
    if new_text != text:
        changes.append("footer certs")
        text = new_text

    if text != orig:
        path.write_text(text, encoding="utf-8")
        return True, changes
    return False, changes


def main() -> None:
    changed: list[str] = []
    for path in sorted(ROOT.rglob("*.html")):
        if "node_modules" in path.parts:
            continue
        ok, items = patch_file(path)
        if ok:
            rel = path.relative_to(ROOT)
            changed.append(f"{rel}: {', '.join(items)}")
    print(f"Updated {len(changed)} files")
    for line in changed:
        print(line)


if __name__ == "__main__":
    main()
