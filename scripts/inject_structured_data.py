#!/usr/bin/env python3
"""Inject deterministic JSON-LD into existing public HTML pages."""
from __future__ import annotations

import json
from pathlib import Path

from structured_data import collection_schema, home_schema, inject, product_schema

ROOT = Path(__file__).resolve().parents[1]


def update(path: Path, payload: dict) -> None:
    html = path.read_text(encoding="utf-8")
    updated = inject(html, payload)
    path.write_text(updated, encoding="utf-8")


def main() -> None:
    data = json.loads((ROOT / "data" / "products.json").read_text(encoding="utf-8"))
    update(ROOT / "index.html", home_schema())
    update(ROOT / "urunler.html", collection_schema(data["products"]))
    count = 0
    for product in data["products"]:
        path = ROOT / "urun" / f"{product['slug']}.html"
        if not path.is_file():
            continue
        update(path, product_schema(product))
        count += 1
    print(f"Injected JSON-LD into homepage, catalog and {count} product pages")


if __name__ == "__main__":
    main()
