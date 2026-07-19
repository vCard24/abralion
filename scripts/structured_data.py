"""Shared JSON-LD builders for Abralion static pages."""
from __future__ import annotations

import json
import re

ORIGIN = "https://abralion.com"
MARKER_START = "<!-- STRUCTURED_DATA_START -->"
MARKER_END = "<!-- STRUCTURED_DATA_END -->"
BLOCK = re.compile(
    rf"\s*{re.escape(MARKER_START)}.*?{re.escape(MARKER_END)}\s*",
    re.S,
)


def inject(html: str, payload: dict) -> str:
    encoded = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).replace(
        "</", "<\\/"
    )
    block = (
        f"\n  {MARKER_START}\n"
        f'  <script type="application/ld+json">{encoded}</script>\n'
        f"  {MARKER_END}\n"
    )
    html = BLOCK.sub("\n", html)
    return html.replace("</head>", f"{block}</head>", 1)


def home_schema() -> dict:
    return {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "Organization",
                "@id": f"{ORIGIN}/#organization",
                "name": "Abralion",
                "legalName": "EKS-PLAST LLC",
                "url": f"{ORIGIN}/",
                "logo": f"{ORIGIN}/assets/images/logo-beyaz-yatay.svg",
                "email": "info@abralion.com",
                "telephone": "+7 985 789-60-62",
            },
            {
                "@type": "WebSite",
                "@id": f"{ORIGIN}/#website",
                "url": f"{ORIGIN}/",
                "name": "Abralion",
                "publisher": {"@id": f"{ORIGIN}/#organization"},
                "inLanguage": "tr",
            },
        ],
    }


def collection_schema(products: list[dict]) -> dict:
    return {
        "@context": "https://schema.org",
        "@type": "CollectionPage",
        "name": "Abralion Ürün Kataloğu",
        "url": f"{ORIGIN}/urunler.html",
        "mainEntity": {
            "@type": "ItemList",
            "numberOfItems": len(products),
            "itemListElement": [
                {
                    "@type": "ListItem",
                    "position": index,
                    "url": f"{ORIGIN}/urun/{product['slug']}.html",
                    "name": product["name"],
                }
                for index, product in enumerate(products, 1)
            ],
        },
        "inLanguage": "tr",
    }


def product_schema(product: dict) -> dict:
    images = [
        f"{ORIGIN}/{image['src'].lstrip('/')}"
        for image in product.get("images", [])
        if image.get("src")
    ]
    url = f"{ORIGIN}/urun/{product['slug']}.html"
    product_node = {
        "@type": "Product",
        "@id": f"{url}#product",
        "name": product["name"],
        "description": product.get("description", ""),
        "url": url,
        "brand": {"@type": "Brand", "name": "Abralion"},
        "category": product.get("categoryName", ""),
    }
    if images:
        product_node["image"] = images
    return {
        "@context": "https://schema.org",
        "@graph": [
            product_node,
            {
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {
                        "@type": "ListItem",
                        "position": 1,
                        "name": "Ana Sayfa",
                        "item": f"{ORIGIN}/",
                    },
                    {
                        "@type": "ListItem",
                        "position": 2,
                        "name": "Ürünler",
                        "item": f"{ORIGIN}/urunler.html",
                    },
                    {
                        "@type": "ListItem",
                        "position": 3,
                        "name": product["name"],
                        "item": url,
                    },
                ],
            },
        ],
    }
