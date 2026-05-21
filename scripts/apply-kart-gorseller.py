# -*- coding: utf-8 -*-
"""Excel/liste ile gelen kart görsellerini kopyalar ve CSS üretir."""
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KART_DIR = ROOT / "urun-kart-gorseller"
ICONS_DIR = Path(r"C:\Users\mosta\Desktop\abralion\icons")
OUT_CSS = ROOT / "assets" / "css" / "product-card-heroes.css"

# (slug, kaynak dosya — None = mevcut kart dosyasına dokunma)
MAPPING = [
    ("metal-inox-kesme-tasi", None),
    ("355mm-metal-sabit-tezgah-kesme-diski", KART_DIR / "abralion--23.jpg"),
    ("metal-inox-taslama-diski", KART_DIR / "abralion--04.jpg"),
    ("zr-zirkon-flap-disk", KART_DIR / "abralion--24.jpg"),
    ("ao-aluminyum-oksit-flap-disk", KART_DIR / "abralion--25.jpg"),
    ("segmentli-standart-elmas-kesici", KART_DIR / "abralion--26.jpg"),
    ("ultra-ince-elmas-disk", KART_DIR / "abralion--08.jpg"),
    ("granit-ve-mermer-segmentli-taslama-diski", KART_DIR / "abralion--09.jpg"),
    ("asfalt-icin-elmas-kesme-diski", KART_DIR / "abralion--10.jpg"),
    ("guclendirilmis-beton-icin-elmas-kesme-diski", KART_DIR / "abralion--11.jpg"),
    ("sds-max-burc-aleti-tarakli-murc", KART_DIR / "abralion--12.jpg"),
    ("hss-matkap-ucu", KART_DIR / "abralion--13.jpg"),
    ("sds-plus-4-kesicili-beton-matkap-ucu-quadro", KART_DIR / "abralion--14.jpg"),
    ("miknatisli-anahtar-ucu-manyetik-somun-adaptoru", KART_DIR / "abralion--16.jpg"),
    ("ph2-manyetik-bits-uc", KART_DIR / "abralion--17.jpg"),
    ("duz-keski-sds-plus", KART_DIR / "abralion--15.jpg"),
    ("duz-keski-sds-max", "icons:01"),
    ("sivri-uclu-keski-murc-sds-plus", "icons:04"),
    ("sivri-uclu-keski-murc-sds-max", "icons:02"),
    ("cok-fonksiyonlu-cam-ve-seramik-matkap-ucu-4-kesicili", "icons:03"),
    ("profesyonel-plastik-maket-bicagi", KART_DIR / "abralion--18.jpg"),
    ("profesyonel-metal-maket-bicagi", KART_DIR / "abralion--19.jpg"),
    ("maket-bicagi-yedek-ucu", KART_DIR / "abralion--20.jpg"),
    ("abs-govdeli-profesyonel-serit-metre", KART_DIR / "abralion--21.jpg"),
]


def resolve_icons(num: str) -> Path:
    pattern = f"*uclar-{num}.jpg"
    for base in (ICONS_DIR, KART_DIR):
        hits = list(base.glob(pattern))
        if hits:
            return hits[0]
    raise FileNotFoundError(f"icons {num} bulunamadi: {pattern}")


def main():
    css_rules = [
        "/* Otomatik üretildi — scripts/apply-kart-gorseller.py */",
        ".product-card-image-container--static-hero {",
        "  height: 200px;",
        "  background-size: cover;",
        "  background-position: center;",
        "  background-repeat: no-repeat;",
        "  filter: grayscale(100%);",
        "  transition: filter 0.4s ease;",
        "}",
        ".product-card:hover .product-card-image-container--static-hero {",
        "  filter: grayscale(0%);",
        "}",
        "",
    ]

    for slug, src in MAPPING:
        dest_dir = ROOT / "assets" / "images" / "products" / slug
        dest_dir.mkdir(parents=True, exist_ok=True)

        if src is None:
            ext = "png" if (dest_dir / f"{slug}-kart.png").exists() else "jpg"
            rel = f"../images/products/{slug}/{slug}-kart.{ext}"
        else:
            if isinstance(src, str) and src.startswith("icons:"):
                src_path = resolve_icons(src.split(":")[1])
            else:
                src_path = Path(src)
            if not src_path.exists():
                raise FileNotFoundError(src_path)
            dest = dest_dir / f"{slug}-kart.jpg"
            shutil.copy2(src_path, dest)
            rel = f"../images/products/{slug}/{slug}-kart.jpg"

        css_rules.append(
            f'.product-card[data-product-id="{slug}"] '
            f".product-card-image-container--static-hero {{\n"
            f"  background-image: url({rel});\n"
            f"}}\n"
        )
        print(f"OK {slug}")

    OUT_CSS.write_text("\n".join(css_rules) + "\n", encoding="utf-8")
    print(f"CSS -> {OUT_CSS}")


if __name__ == "__main__":
    main()
