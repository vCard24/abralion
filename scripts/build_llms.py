#!/usr/bin/env python3
"""Generate agent-friendly llms.txt files from the product catalogs (TR + RU)."""
from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://abralion.com"


def summary(text: str, limit: int = 150) -> str:
    clean = " ".join((text or "").split())
    if len(clean) <= limit:
        return clean
    return clean[: limit - 1].rstrip() + "…"


def write_tr(data: dict) -> None:
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
        f"- [Русская версия]({BASE}/ru/): Русскоязычный каталог Abralion.",
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
            f"- Sitemap (TR): {BASE}/sitemap.xml",
            f"- Sitemap (RU): {BASE}/ru/sitemap.xml",
            f"- Robots: {BASE}/robots.txt",
            f"- LLMs (RU): {BASE}/ru/llms.txt",
        ]
    )
    out = ROOT / "llms.txt"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {out.relative_to(ROOT)} ({len(data['products'])} products)")


def write_ru(data: dict) -> None:
    lines = [
        "# Abralion",
        "> B2B-каталог EKS-PLAST LLC: промышленные решения для резки, шлифования, сверления и измерений для турецких компаний в России.",
        "",
        "Abralion предлагает семейства профессиональных абразивных и режущих инструментов с техническими характеристиками, вариантами и областями применения.",
        "",
        "## Основные страницы",
        f"- [Главная]({BASE}/ru/): Компания, линейки продуктов и контакты.",
        f"- [Каталог продукции]({BASE}/ru/produkty.html): Все семейства продуктов и фильтры категорий.",
        f"- [Документы]({BASE}/ru/dokumenty.html): Каталоги и технические файлы.",
        f"- [О компании]({BASE}/ru/o-kompanii.html): EKS-PLAST LLC и бренд Abralion.",
        f"- [Контакты]({BASE}/ru/kontakty.html): Телефон, e-mail и запрос цены.",
        f"- [Türkçe sürüm]({BASE}/): Турецкая версия каталога Abralion.",
        "",
        "## Категории",
    ]
    for category in sorted(data["categories"], key=lambda item: item["order"]):
        url = f"{BASE}/ru/produkty.html?kategori={quote(category['id'])}"
        lines.append(f"- [{category['name']}]({url})")

    lines.extend(["", "## Семейства продуктов"])
    for product in sorted(data["products"], key=lambda item: item["name"]):
        url = f"{BASE}/ru/urun/{product['slug']}.html"
        lines.append(f"- [{product['name']}]({url}): {summary(product.get('description', ''))}")

    lines.extend(
        [
            "",
            "## Контакты",
            "- E-mail: info@abralion.com",
            "- Телефон: +7 985 789-60-62",
            f"- Web: {BASE}/ru/",
            "",
            "## Источники для обхода",
            f"- Sitemap (RU): {BASE}/ru/sitemap.xml",
            f"- Sitemap (TR): {BASE}/sitemap.xml",
            f"- Robots: {BASE}/robots.txt",
            f"- LLMs (TR): {BASE}/llms.txt",
        ]
    )
    out = ROOT / "ru" / "llms.txt"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {out.relative_to(ROOT)} ({len(data['products'])} products)")


def main() -> None:
    tr = json.loads((ROOT / "data" / "products.json").read_text(encoding="utf-8"))
    ru = json.loads((ROOT / "ru" / "data" / "products.json").read_text(encoding="utf-8"))
    write_tr(tr)
    write_ru(ru)


if __name__ == "__main__":
    main()
