#!/usr/bin/env python3
"""Validate, sync, and publish Abralion product catalog (source -> min.js)."""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "assets" / "js" / "products-data.js"
ROOT_COPY = ROOT / "products-data.js"
MIN_OUTPUT = ROOT / "assets" / "js" / "products-data.min.js"
CATALOG_RE = re.compile(
    r"window\.ABRALION_CATALOG\s*=\s*(\{.*\})\s*;?\s*$",
    re.S,
)
HEADER = (
    "/* Abralion ürün kataloğu — düzenleme dosyası: assets/js/products-data.js\n"
    "   Değişiklikten sonra: npm run sync:catalog\n"
    "   Site products-data.min.js yükler; bu dosyayı doğrudan HTML'e bağlamayın. */\n"
)


def parse_catalog(text: str) -> dict:
    match = CATALOG_RE.search(text)
    if not match:
        raise ValueError("window.ABRALION_CATALOG bulunamadı")
    return json.loads(match.group(1))


def ensure_header(text: str) -> str:
    if "npm run sync:catalog" in text[:400]:
        return text
    body = text.lstrip()
    if body.startswith("/*"):
        end = body.find("*/")
        if end != -1:
            body = body[end + 2 :].lstrip()
    return HEADER + body


def validate(catalog: dict) -> list[str]:
    issues: list[str] = []
    categories = catalog.get("categories") or []
    products = catalog.get("products") or []
    cat_ids = {c.get("id") for c in categories if c.get("id")}

    if not categories:
        issues.append("Kategori listesi boş")
    if not products:
        issues.append("Ürün listesi boş")

    slugs: list[str] = []
    for product in products:
        slug = product.get("slug") or product.get("id")
        if not slug:
            issues.append("Slug/id eksik ürün var")
            continue
        slugs.append(slug)
        if product.get("categoryId") not in cat_ids:
            issues.append(f"{slug}: geçersiz categoryId ({product.get('categoryId')})")
        if not Path(f"urun/{slug}.html").exists():
            issues.append(f"{slug}: urun/{slug}.html yok")
        for image in product.get("images") or []:
            src = image.get("src")
            if src and not Path(src).exists():
                issues.append(f"{slug}: görsel yok ({src})")

    dupes = sorted({s for s in slugs if slugs.count(s) > 1})
    for slug in dupes:
        issues.append(f"Yinelenen slug: {slug}")

    return issues


def write_source(catalog: dict, pretty: bool) -> None:
    payload = json.dumps(catalog, ensure_ascii=False, indent=2 if pretty else None)
    if not pretty:
        payload = payload.replace(",", ", ")
    text = ensure_header(f"window.ABRALION_CATALOG = {payload};\n")
    SOURCE.write_text(text, encoding="utf-8")
    ROOT_COPY.write_text(text, encoding="utf-8")


def minify() -> None:
    script = ROOT / "scripts" / "minify_products_data.py"
    subprocess.run([sys.executable, str(script)], cwd=ROOT, check=True)


def bump_cache(version: str) -> None:
    pat = re.compile(r"products-data\.min\.js\?v=[^\"']+")
    rep = f"products-data.min.js?v={version}"
    count = 0
    for path in ROOT.rglob("*.html"):
        if "node_modules" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        new_text = pat.sub(rep, text)
        if new_text != text:
            path.write_text(new_text, encoding="utf-8")
            count += 1
    print(f"Cache bust: {count} HTML -> {rep}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync Abralion product catalog")
    parser.add_argument(
        "--from-root",
        action="store_true",
        help="Kök products-data.js dosyasını kaynak kabul et",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="JSON'u okunabilir biçimde yeniden yaz",
    )
    parser.add_argument(
        "--bump-cache",
        metavar="VERSION",
        help="HTML'deki products-data.min.js sürümünü güncelle (ör. 20260704)",
    )
    args = parser.parse_args()

    src_path = ROOT_COPY if args.from_root else SOURCE
    if not src_path.is_file():
        print(f"Kaynak bulunamadı: {src_path}", file=sys.stderr)
        return 1

    text = src_path.read_text(encoding="utf-8")
    try:
        catalog = parse_catalog(text)
    except (ValueError, json.JSONDecodeError) as exc:
        print(f"Katalog okunamadı: {exc}", file=sys.stderr)
        return 1

    issues = validate(catalog)
    if issues:
        print("Doğrulama uyarıları:")
        for item in issues:
            print(f"  - {item}")
    else:
        print("Doğrulama: OK")

    if args.pretty or src_path == ROOT_COPY:
        write_source(catalog, pretty=args.pretty or src_path == ROOT_COPY)
        print(f"Kaynak yazıldı: {SOURCE.relative_to(ROOT)} + {ROOT_COPY.name}")
    elif src_path == SOURCE and SOURCE.read_text(encoding="utf-8") != ROOT_COPY.read_text(encoding="utf-8"):
        ROOT_COPY.write_text(SOURCE.read_text(encoding="utf-8"), encoding="utf-8")
        print(f"Kök kopya güncellendi: {ROOT_COPY.name}")

    minify()

    cats = catalog.get("categories") or []
    prods = catalog.get("products") or []
    print(f"Katalog: {len(cats)} kategori, {len(prods)} ürün")

    if args.bump_cache:
        bump_cache(args.bump_cache)

    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
