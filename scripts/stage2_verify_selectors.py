#!/usr/bin/env python3
"""Verify suspicious CSS selectors on live pages via local HTTP + Playwright."""
from __future__ import annotations

import json
import sys
import threading
import time
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# 14 şüpheli selektör grubu — gerçek DOM + JS render senaryoları
CHECKS = [
    ("urun/metal-inox-kesme-tasi.html", ".specs-table--stitch", "border-collapse", None),
    ("urun/metal-inox-kesme-tasi.html", "#variant-specs-table .specs-table th", "font-weight", None),
    ("urun/metal-inox-kesme-tasi.html", ".product-detail-tab[aria-selected='true']", "border-bottom-width", None),
    ("urun/metal-inox-kesme-tasi.html", ".product-detail-tabs-section", "display", None),
    ("urun/metal-inox-kesme-tasi.html", ".page-product-detail #variant-specs-table .specs-table", "width", None),
    ("karsilastir.html", ".compare-table", "border-collapse", "compare"),
    ("karsilastir.html", ".compare-table-wrapper", "overflow-x", "compare"),
    ("karsilastir.html", ".compare-table th", "font-weight", "compare"),
    ("index.html", ".home-hero-section", "min-height", None),
    ("index.html", "section.py-section-gap", "padding-top", None),
    ("hakkimizda.html", "section.py-section-gap", "padding-top", None),
    ("urunler.html", "#products-grid", "display", "catalog"),
    ("dokumanlar.html", ".page-documents .docs-hero-stat", "border-radius", None),
    ("fiyat-teklifi.html", ".quote-sheet", "border-radius", None),
]


def main() -> int:
    from playwright.sync_api import sync_playwright

    port = 8765
    server = ThreadingHTTPServer(("127.0.0.1", port), SimpleHTTPRequestHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    time.sleep(0.4)
    base = f"http://127.0.0.1:{port}"

    results: list[dict] = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        for rel, selector, prop, mode in CHECKS:
            url = f"{base}/{rel}"
            entry = {"url": rel, "selector": selector, "property": prop, "mode": mode}
            try:
                if mode == "compare":
                    page.goto(f"{base}/", wait_until="domcontentloaded")
                    page.evaluate(
                        """() => {
                          localStorage.setItem('abralion_compare_list', JSON.stringify([
                            'metal-inox-kesme-tasi::260-115',
                            'segmentli-standart-elmas-kesici::1453-1'
                          ]));
                        }"""
                    )
                page.goto(url, wait_until="domcontentloaded", timeout=30000)
                if mode == "compare":
                    page.wait_for_selector(".compare-table", timeout=15000)
                elif mode == "catalog":
                    page.wait_for_selector("#products-grid .product-card", timeout=15000)
                else:
                    page.wait_for_timeout(600)
                el = page.query_selector(selector)
                if not el:
                    entry.update(ok=False, reason="element not found", value="")
                else:
                    value = page.evaluate(
                        "(args) => getComputedStyle(args.el).getPropertyValue(args.prop)",
                        {"el": el, "prop": prop},
                    )
                    value = str(value).strip()
                    ok = bool(value) and value not in ("none", "normal")
                    if prop in ("display", "width", "min-height", "padding-top", "border-radius", "overflow-x"):
                        ok = bool(value)
                    if prop == "overflow-x" and value == "auto":
                        ok = True
                    entry.update(ok=ok, value=value, reason="" if ok else "empty/unexpected style")
            except Exception as exc:
                entry.update(ok=False, reason=str(exc), value="")
            results.append(entry)
        browser.close()
    server.shutdown()

    failed = [r for r in results if not r.get("ok")]
    print(f"Verified {len(results)} checks, failed {len(failed)}")
    for r in results:
        mark = "OK" if r.get("ok") else "FAIL"
        print(f"  [{mark}] {r['url']} :: {r['selector']} -> {r['property']}={r.get('value','')}")
        if r.get("reason") and not r.get("ok"):
            print(f"         {r['reason']}")

    out = ROOT / "scripts" / "stage2_selector_verify.json"
    out.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
