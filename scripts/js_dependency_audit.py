#!/usr/bin/env python3
"""Audit JS global dependencies and HTML script load order."""
from __future__ import annotations

import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
JS_DIR = ROOT / "assets" / "js"
OUT = ROOT / "scripts" / "js_dependency_map.md"

SCRIPT_RE = re.compile(
    r'<script(?:\s+defer)?\s+src="([^"]+assets/js/[^"?]+\.js)(?:\?v=[^"]+)?"',
    re.I,
)
SCRIPT_SYNC_RE = re.compile(
    r'<script\s+src="([^"]+assets/js/[^"?]+\.js)(?:\?v=[^"]+)?"',
    re.I,
)

# Global symbol -> defining script (basename)
DEFINES: dict[str, str] = {
    "getBasePath": "site.js",
    "productUrl": "site.js",
    "productMenuThumbUrl": "site.js",
    "productThumbUrl": "site.js",
    "sendFormMail": "site.js",
    "readCompareListFromStorage": "site.js",
    "encodeCompareKeysForUrl": "site.js",
    "parseModelsFromUrl": "site.js",
    "buildQuotePageUrl": "site.js",
    "navigateToQuotePage": "site.js",
    "saveComparePrefillForQuote": "site.js",
    "readComparePrefillForQuote": "site.js",
    "collectCompareKeysForQuote": "site.js",
    "resolveCatalogKeys": "site.js",
    "getCompareKeysForPrefill": "site.js",
    "isQuoteFromCompare": "site.js",
    "sanitizeDownloadLabel": "site.js",
    "documentDownloadFilename": "site.js",
    "initPdfLinks": "site.js",
    "initPdfDownloadLinks": "site.js",
    "AbralionIcons": "icons.js",
    "bindProductImageFallback": "product-image-utils.js",
    "bindGalleryImageFallback": "product-image-utils.js",
    "buildProductImageCandidates": "product-image-utils.js",
    "primaryProductImageSrc": "product-image-utils.js",
    "productImageRelForFetch": "product-image-utils.js",
    "ABRALION_IMAGE": "product-image-utils.js",
    "ABRALION_CATALOG": "products-data.min.js",
    "getTableColumns": "VariantDisplay.js",
    "getSpecColumnClass": "VariantDisplay.js",
    "variantRowCells": "VariantDisplay.js",
    "variantSpecLines": "VariantDisplay.js",
    "variantLabel": "VariantDisplay.js",
    "CompareManager": "CompareManager.js",
    "compareManager": "CompareManager.js",
    "QuoteManager": "QuoteManager.js",
    "quoteManager": "QuoteManager.js",
    "ProductManager": "ProductManager.js",
    "ProductCard": "ProductCard.js",
    "FormValidator": "FormValidator.js",
    "Header": "Header.js",
    "MegaMenu": "MegaMenu.js",
    "initProductGallery": "product-gallery.js",
    "initGalleryLightbox": "gallery-lightbox.js",
    "GalleryLightbox": "gallery-lightbox.js",
    "setPageSocialMeta": "og-meta.js",
    "productOgImage": "og-meta.js",
    "ensureAbralionPdfLogoDataUrl": "quote-pdf-logo.js",
}

# script basename -> globals it needs loaded before it runs
REQUIRES: dict[str, set[str]] = {
    "site.js": {"getBasePath"},  # self-contained after load
    "product-image-utils.js": set(),
    "og-meta.js": {"getBasePath"},
    "products-data.min.js": set(),
    "VariantDisplay.js": set(),
    "CompareManager.js": set(),
    "QuoteManager.js": set(),
    "ProductManager.js": {"getBasePath", "ABRALION_CATALOG"},
    "ProductCard.js": {"ProductManager", "compareManager", "productThumbUrl", "productUrl", "AbralionIcons"},
    "FormValidator.js": set(),
    "Header.js": {"AbralionIcons", "getBasePath"},
    "MegaMenu.js": {"getBasePath", "bindGalleryImageFallback", "AbralionIcons", "productMenuThumbUrl", "productThumbUrl", "productUrl"},
    "product-gallery.js": set(),
    "gallery-lightbox.js": set(),
    "product-detail.js": {
        "getBasePath",
        "ABRALION_CATALOG",
        "ProductManager",
        "compareManager",
        "buildProductImageCandidates",
        "bindGalleryImageFallback",
        "initProductGallery",
        "initGalleryLightbox",
        "getTableColumns",
        "getSpecColumnClass",
        "variantRowCells",
        "variantSpecLines",
        "variantLabel",
        "setPageSocialMeta",
        "productUrl",
        "AbralionIcons",
    },
    "main.js": {"Header", "compareManager"},
    "pages/home.js": {"ProductManager", "ProductCard", "bindProductImageFallback", "getBasePath"},
    "pages/urunler.js": {"ProductManager", "ProductCard", "compareManager", "getBasePath", "AbralionIcons"},
    "pages/karsilastir.js": {
        "getBasePath",
        "compareManager",
        "quoteManager",
        "ProductManager",
        "variantSpecLines",
        "navigateToQuotePage",
        "buildQuotePageUrl",
        "AbralionIcons",
        "ensureAbralionPdfLogoDataUrl",
    },
    "pages/fiyat-teklifi.js": {
        "getBasePath",
        "sendFormMail",
        "quoteManager",
        "ProductManager",
        "FormValidator",
        "variantSpecLines",
        "variantLabel",
        "resolveCatalogKeys",
        "isQuoteFromCompare",
        "ensureAbralionPdfLogoDataUrl",
        "AbralionIcons",
    },
    "pages/contact.js": {"sendFormMail", "FormValidator", "getBasePath"},
    "quote-pdf-logo.js": set(),
    "icons.js": set(),
}


def basename(src: str) -> str:
    return src.replace("\\", "/").split("/")[-1].split("?")[0]


def scripts_in_html(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    found: list[tuple[int, str]] = []
    for m in SCRIPT_SYNC_RE.finditer(text):
        found.append((m.start(), basename(m.group(1))))
    for m in SCRIPT_RE.finditer(text):
        found.append((m.start(), basename(m.group(1))))
    found.sort(key=lambda x: x[0])
    # dedupe preserving order
    seen: set[str] = set()
    ordered: list[str] = []
    for _, name in found:
        if name not in seen:
            seen.add(name)
            ordered.append(name)
    return ordered


def available_before(scripts: list[str], index: int) -> set[str]:
    avail: set[str] = set()
    for name in scripts[:index]:
        for sym, src in DEFINES.items():
            if src == name:
                avail.add(sym)
    return avail


def audit_page(path: Path, scripts: list[str]) -> list[str]:
    issues: list[str] = []
    for i, script in enumerate(scripts):
        needs = REQUIRES.get(script, set())
        if not needs:
            continue
        avail = available_before(scripts, i)
        # symbols defined in same file or earlier scripts
        for sym in sorted(needs):
            provider = DEFINES.get(sym)
            if provider is None:
                continue
            if sym not in avail and provider != script:
                try:
                    provider_idx = scripts.index(provider)
                except ValueError:
                    issues.append(f"{script}: `{sym}` gerekli ({provider} eksik)")
                    continue
                if provider_idx >= i:
                    issues.append(
                        f"{script}: `{sym}` gerekli; {provider} sonra yükleniyor "
                        f"(sıra {provider_idx + 1} > {i + 1})"
                    )
    return issues


def scan_js_consumes() -> dict[str, set[str]]:
    """Rough scan: which tracked globals each file references."""
    tracked = set(DEFINES)
    by_file: dict[str, set[str]] = defaultdict(set)
    for path in sorted(JS_DIR.rglob("*.js")):
        if "vendor" in path.parts or path.name in ("products-data.js", "products-data.min.js"):
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for sym in tracked:
            if sym == "getBasePath" and path.name == "site.js":
                continue
            if re.search(rf"\b{re.escape(sym)}\b", text):
                by_file[path.name].add(sym)
    return by_file


def write_map(pages: dict[str, list[str]], page_issues: dict[str, list[str]]) -> None:
    consumes = scan_js_consumes()
    lines = [
        "# JS global bağımlılık haritası",
        "",
        "Otomatik üretim: `python scripts/js_dependency_audit.py`",
        "",
        "## Sembol → tanımlayan dosya",
        "",
        "| Global | Dosya |",
        "|--------|-------|",
    ]
    for sym in sorted(DEFINES):
        lines.append(f"| `{sym}` | `{DEFINES[sym]}` |")

    lines.extend(["", "## Dosya → tükettiği globaller (tarama)", ""])
    for fname in sorted(consumes):
        syms = ", ".join(f"`{s}`" for s in sorted(consumes[fname]))
        lines.append(f"- **{fname}**: {syms or '—'}")

    lines.extend(["", "## Sayfa script sırası", ""])
    for rel in sorted(pages):
        scripts = pages[rel]
        lines.append(f"### `{rel}`")
        lines.append("")
        for i, s in enumerate(scripts, 1):
            lines.append(f"{i}. `{s}`")
        issues = page_issues.get(rel, [])
        if issues:
            lines.append("")
            lines.append("**Sıra sorunları:**")
            for item in issues:
                lines.append(f"- {item}")
        lines.append("")

    lines.extend(
        [
            "## Önerilen temel sıra (ürün / liste sayfaları)",
            "",
            "1. `icons.js`",
            "2. `product-image-utils.js` (site.js öncesi)",
            "3. `site.js`",
            "4. `products-data.min.js` (senkron, defer yok)",
            "5. `VariantDisplay.js` (ürün detay / karşılaştır / teklif)",
            "6. `CompareManager.js` → `QuoteManager.js` (gerektiğinde)",
            "7. `ProductManager.js` → `ProductCard.js` (gerektiğinde)",
            "8. `FormValidator.js` (form sayfaları)",
            "9. `Header.js` → `MegaMenu.js`",
            "10. `product-gallery.js` → `gallery-lightbox.js` (ürün detay)",
            "11. `og-meta.js` (ürün detay)",
            "12. `main.js` → sayfa modülü",
            "",
        ]
    )

    OUT.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    pages: dict[str, list[str]] = {}
    all_issues: dict[str, list[str]] = {}
    total = 0

    for html in sorted(ROOT.rglob("*.html")):
        if "node_modules" in html.parts:
            continue
        scripts = scripts_in_html(html)
        if not scripts:
            continue
        rel = str(html.relative_to(ROOT)).replace("\\", "/")
        pages[rel] = scripts
        issues = audit_page(html, scripts)
        if issues:
            all_issues[rel] = issues
            total += len(issues)

    write_map(pages, all_issues)

    print(f"Wrote {OUT.relative_to(ROOT)} ({len(pages)} sayfa)")
    if total:
        print(f"Script sırası sorunları: {total}")
        for rel, issues in sorted(all_issues.items()):
            for item in issues:
                print(f"  {rel}: {item}")
        return 1
    print("Script sırası: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
