#!/usr/bin/env python3
"""Generate an agent-friendly llms.txt from the canonical product catalog."""
from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://abralion.com"
CATALOG = ROOT / "data" / "products.json"
OUTPUT = ROOT / "llms.txt"


def summary(text: str, limit: int = 150) -> str:
    clean = " ".join((text or "").split())
    if len(clean) <= limit:
        return clean
    return clean[: limit - 1].rstrip() + "…"


def main() -> None:
    data = json.loads(CATALOG.read_text(encoding="utf-8"))
    lines = [
        "# Abralion",
        "> Rusya'daki Türk firmalarına endüstriyel kesim, taşlama, delme ve ölçüm ürünleri sunan EKS-PLAST LLC B2B kataloğu.",
        "",
        "Abralion; teknik özellikleri, varyasyonları ve uygulama alanları açıklanmış profesyonel aşındırıcı ve kesici ürün aileleri sunar.",
        "",
        "## Temel sayfalar",
        f"- [Ana sayfa]({BASE}/): Firma, ürün aileleri ve iletişim özeti.",
        f"- [Ürün kataloğu]({BASE}/urunler.html): Tüm ürün aileleri ve kategori filtreleri.",
        f"- [Teknik dokümanlar]({BASE}/dokumanlar.html): Katalog ve teknik dosyalar.",
        f"- [Hakkımızda]({BASE}/hakkimizda.html): EKS-PLAST LLC ve Abralion bilgileri.",
        f"- [İletişim]({BASE}/iletisim.html): Telefon, e-posta ve teklif kanalları.",
        "",
        "## Kategoriler",
    ]
    for category in sorted(data["categories"], key=lambda item: item["order"]):
        url = f"{BASE}/urunler.html?kategori={quote(category['id'])}"
        lines.append(f"- [{category['name']}]({url})")

    lines.extend(["", "## Ürün aileleri"])
    for product in sorted(data["products"], key=lambda item: item["name"]):
        url = f"{BASE}/urun/{product['slug']}.html"
        lines.append(f"- [{product['name']}]({url}): {summary(product.get('description', ''))}")

    lines.extend(
        [
            "",
            "## İletişim",
            "- E-posta: info@abralion.com",
            "- Telefon: +7 985 789-60-62",
            f"- Web: {BASE}/",
            "",
            "## Tarama kaynakları",
            f"- Sitemap: {BASE}/sitemap.xml",
            f"- Robots: {BASE}/robots.txt",
        ]
    )
    OUTPUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {OUTPUT.relative_to(ROOT)} ({len(data['products'])} products)")


if __name__ == "__main__":
    main()
