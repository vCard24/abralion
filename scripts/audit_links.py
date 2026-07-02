#!/usr/bin/env python3
"""Audit local asset references across HTML, CSS, JS and catalog data."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parent.parent
SKIP_DIRS = {"node_modules", ".git", ".cursor-psi", "vendor"}

# Linked only in Stage 2 selector audit — not deployed
SKIP_FILES = {
    "assets/css/product-card-heroes.css",
    "assets/css/product-detail-page.css",
}

CATALOG_JS = {
    "assets/js/products-data.js",
    "assets/js/products-data.min.js",
}

REF_PATTERNS = [
    re.compile(r"""href\s*=\s*["']([^"']+)["']""", re.I),
    re.compile(r"""src\s*=\s*["']([^"']+)["']""", re.I),
    re.compile(r"""srcset\s*=\s*["']([^"']+)["']""", re.I),
    re.compile(r"""imagesrcset\s*=\s*["']([^"']+)["']""", re.I),
    re.compile(r"""url\(\s*['"]?([^'")\s]+)""", re.I),
    re.compile(r"""fetch\(\s*['"]([^'"]+)['"]""", re.I),
]

JS_STATIC_PATH = re.compile(
    r"""['"]((?:assets|data|urun)/[^'"${}\\]+)['"]""",
)

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".avif", ".svg", ".ico", ".pdf"}
ASSET_EXT = re.compile(
    r"\.(html?|css|js|mjs|jpe?g|png|gif|webp|avif|svg|ico|pdf|json|woff2?|ttf|eot|zip|webmanifest)$",
    re.I,
)


def is_deploy_html(path: Path) -> bool:
    return path.suffix == ".html" and "scripts" not in path.parts


def iter_source_files() -> list[Path]:
    files: list[Path] = []
    for pattern in ("*.html", "*.css", "*.js", "*.json", "*.xml"):
        for p in ROOT.rglob(pattern):
            if p.is_file() and not any(s in p.parts for s in SKIP_DIRS):
                rel = p.relative_to(ROOT).as_posix()
                if rel in SKIP_FILES:
                    continue
                if pattern == "*.html" and not is_deploy_html(p):
                    continue
                files.append(p)
    return sorted(set(files))


def is_external(ref: str) -> bool:
    ref = ref.strip()
    return (
        not ref
        or ref.startswith("#")
        or ref.startswith(("mailto:", "tel:", "javascript:", "data:"))
        or ref.startswith(("http://", "https://", "//"))
    )


def is_checkable_ref(ref: str) -> bool:
    ref = ref.strip()
    if is_external(ref):
        return False
    if "${" in ref or "`" in ref or "{" in ref or "}" in ref:
        return False
    if ref in (".", ".."):
        return False
    if ref.startswith(("assets/", "data/", "urun/", "../", "./", "/")):
        return True
    return bool(ASSET_EXT.search(ref.split("?")[0].split("#")[0]))


def normalize_ref(ref: str, base: Path) -> str | None:
    ref = unquote(ref.strip())
    if not is_checkable_ref(ref):
        return None
    ref = ref.split("?")[0].split("#")[0]
    if not ref:
        return None
    if ref.startswith(("assets/", "data/", "urun/")):
        target = ROOT / ref
    elif ref.startswith("/"):
        target = ROOT / ref.lstrip("/")
    else:
        target = (base.parent / ref).resolve()
    try:
        return target.relative_to(ROOT.resolve()).as_posix()
    except ValueError:
        return None


def extract_refs(text: str, base: Path) -> set[str]:
    refs: set[str] = set()
    for pat in REF_PATTERNS:
        for m in pat.finditer(text):
            raw = m.group(1)
            if pat.pattern.startswith("srcset") or "imagesrcset" in pat.pattern:
                for part in raw.split(","):
                    chunk = part.strip().split()
                    if chunk:
                        rel = normalize_ref(chunk[0], base)
                        if rel:
                            refs.add(rel)
            else:
                rel = normalize_ref(raw, base)
                if rel:
                    refs.add(rel)

    if base.suffix == ".js":
        for m in JS_STATIC_PATH.finditer(text):
            rel = normalize_ref(m.group(1), base)
            if rel:
                refs.add(rel)
    return refs


def load_catalog() -> dict:
    raw = (ROOT / "assets/js/products-data.js").read_text(encoding="utf-8")
    m = re.search(r"window\.ABRALION_CATALOG\s*=\s*(\{.*\})\s*;?\s*$", raw, re.S)
    return json.loads(m.group(1))


def catalog_missing_on_disk(catalog: dict) -> list[tuple[str, str]]:
    """Paths referenced by JS/catalog conventions that must exist."""
    missing: list[tuple[str, str]] = []
    for product in catalog.get("products", []):
        slug = product.get("slug") or ""
        if not slug:
            continue
        folder = ROOT / f"assets/images/products/{slug}"
        kart = folder / f"{slug}-kart.jpg"
        if kart.is_file():
            continue
        missing.append((f"catalog:{slug}", kart.relative_to(ROOT).as_posix()))

        for img in product.get("images") or []:
            src = (img.get("src") or "").lstrip("/")
            if src.startswith("assets/"):
                p = ROOT / src
                if not p.is_file():
                    missing.append((f"catalog:{slug}", src))

        app = (product.get("applicationImage") or "").lstrip("/")
        if app.startswith("assets/") and not (ROOT / app).is_file():
            missing.append((f"catalog:{slug}", app))

        doc = (product.get("technicalCatalog") or "").lstrip("/")
        if doc.startswith("assets/") and not (ROOT / doc).is_file():
            missing.append((f"catalog:{slug}", doc))

    placeholder = ROOT / "assets/images/products/placeholder-kart.jpg"
    if not placeholder.is_file():
        missing.append(("catalog", "assets/images/products/placeholder-kart.jpg"))
    return missing


def ref_exists(rel: str) -> bool:
    if rel in (".", ""):
        return (ROOT / "index.html").is_file()
    target = ROOT / rel
    if target.is_file():
        return True
    if target.is_dir():
        return (target / "index.html").is_file()
    return False


def audit() -> tuple[list[dict], list[dict]]:
    broken: list[dict] = []
    checked: list[dict] = []

    for path in iter_source_files():
        rel_path = path.relative_to(ROOT).as_posix()
        if rel_path in CATALOG_JS:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for rel in sorted(extract_refs(text, path)):
            ok = ref_exists(rel)
            entry = {
                "source": path.relative_to(ROOT).as_posix(),
                "ref": rel,
                "ok": ok,
            }
            checked.append(entry)
            if not ok:
                broken.append(entry)

    catalog = load_catalog()
    for slug_path, rel in catalog_missing_on_disk(catalog):
        if not ref_exists(rel):
            broken.append({"source": slug_path, "ref": rel, "ok": False, "catalog": True})
            checked.append({"source": slug_path, "ref": rel, "ok": False, "catalog": True})

    seen: set[tuple[str, str]] = set()
    unique_broken: list[dict] = []
    for b in broken:
        key = (b["source"], b["ref"])
        if key in seen:
            continue
        seen.add(key)
        unique_broken.append(b)
    return unique_broken, checked


def main() -> int:
    broken, checked = audit()
    print(f"Checked references: {len(checked)}")
    print(f"Broken references: {len(broken)}")
    if broken:
        print("\nBROKEN:")
        for b in broken:
            tag = " [catalog]" if b.get("catalog") else ""
            print(f"  [{b['source']}]{tag} -> {b['ref']}")
        return 1
    print("OK: zero broken references")
    return 0


if __name__ == "__main__":
    sys.exit(main())
