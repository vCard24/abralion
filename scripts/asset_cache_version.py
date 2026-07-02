#!/usr/bin/env python3
"""Content-hash cache bust (?v=<md5 first 8 chars>) for versioned static assets."""
from __future__ import annotations

import hashlib
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# href/src references like ../assets/js/foo.js?v=anything
VERSIONED_REF = re.compile(
    r"""((?:\.\./)?assets/(?:css|js)/([^"'\s>?#]+\.(?:css|js)))\?v=[^"'\s>]+""",
    re.I,
)

# Add ?v= when missing
BARE_REF_PATTERNS = (
    re.compile(r"((?:\.\./)?assets/css/bundle\.min\.css)(?!\?v=)"),
    re.compile(r"((?:\.\./)?assets/js/icons\.js)(?!\?v=)"),
)

BARE_ASSET_REF = re.compile(
    r"""((?:\.\./)?assets/(?:css|js)/([^"'\s>?#]+\.(?:css|js)))(?!\?v=)""",
    re.I,
)

SKIP_VERSION = frozenset(
    {
        "vendor/html2canvas.min.js",
        "vendor/jspdf.umd.min.js",
        "products-data.js",
        "products-data.min.js",
    }
)


def content_hash(path: Path, length: int = 8) -> str:
    data = path.read_bytes()
    return hashlib.md5(data).hexdigest()[:length]


def resolve_asset_path(html_path: Path, rel_asset: str) -> Path | None:
    """rel_asset e.g. assets/js/icons.js or ../assets/js/icons.js"""
    rel = rel_asset.replace("\\", "/")
    if rel.startswith("../"):
        if "templates" in html_path.parts:
            # Generator şablonları urun/*.html yolunu kullanır
            base = (ROOT / "urun" / rel).resolve()
        else:
            base = (html_path.parent / rel).resolve()
    else:
        base = (ROOT / rel).resolve()
    try:
        base.relative_to(ROOT.resolve())
    except ValueError:
        return None
    return base if base.is_file() else None


def bump_versioned_assets_in_html(
    root: Path = ROOT,
    *,
    only_files: set[str] | None = None,
) -> dict[str, str]:
    """Update ?v= on all versioned asset refs from file content hashes.

    Returns mapping basename -> hash for assets that were updated.
    """
    hashes: dict[str, str] = {}
    changed_files: list[Path] = []

    for html_path in sorted(root.rglob("*.html")):
        if "node_modules" in html_path.parts:
            continue
        text = html_path.read_text(encoding="utf-8")
        orig = text

        def repl(m: re.Match[str]) -> str:
            prefix = m.group(1)
            filename = m.group(2).replace("\\", "/")
            if only_files and filename not in only_files:
                return m.group(0)
            asset_path = resolve_asset_path(html_path, prefix)
            if not asset_path:
                return m.group(0)
            h = hashes.get(filename)
            if h is None:
                h = content_hash(asset_path)
                hashes[filename] = h
            return f"{prefix}?v={h}"

        text = VERSIONED_REF.sub(repl, text)

        def bare_asset_repl(m: re.Match[str]) -> str:
            prefix = m.group(1)
            filename = m.group(2).replace("\\", "/")
            if filename in SKIP_VERSION or filename.startswith("vendor/"):
                return m.group(0)
            if only_files and filename not in only_files:
                return m.group(0)
            asset_path = resolve_asset_path(html_path, prefix)
            if not asset_path:
                return m.group(0)
            h = hashes.get(filename)
            if h is None:
                h = content_hash(asset_path)
                hashes[filename] = h
            return f"{prefix}?v={h}"

        if only_files is None:
            text = BARE_ASSET_REF.sub(bare_asset_repl, text)

        if only_files is None or only_files & {"bundle.min.css", "icons.js"}:
            for bare_pat in BARE_REF_PATTERNS:
                def bare_repl(m: re.Match[str], _pat=bare_pat) -> str:
                    prefix = m.group(1)
                    name = prefix.split("/")[-1]
                    if only_files and name not in only_files:
                        return m.group(0)
                    asset_path = resolve_asset_path(html_path, prefix)
                    if not asset_path:
                        return m.group(0)
                    h = hashes.get(name)
                    if h is None:
                        h = content_hash(asset_path)
                        hashes[name] = h
                    return f"{prefix}?v={h}"

                text = bare_pat.sub(bare_repl, text)

        if text != orig:
            html_path.write_text(text, encoding="utf-8")
            changed_files.append(html_path)

    return hashes


if __name__ == "__main__":
    versions = bump_versioned_assets_in_html()
    print(f"Updated cache keys for {len(versions)} assets")
    for name in sorted(versions):
        print(f"  {name} ?v={versions[name]}")
