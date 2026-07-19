#!/usr/bin/env python3
"""Build compact Turkish fonts and responsive homepage card images."""
from __future__ import annotations

import io
import ssl
import urllib.request
from pathlib import Path

import pillow_avif  # noqa: F401
from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
FONT_DIR = ROOT / "assets" / "fonts"
FONT_CSS = ROOT / "assets" / "css" / "fonts.css"

FONT_SOURCES = {
    "Inter": "https://raw.githubusercontent.com/google/fonts/main/ofl/inter/Inter%5Bopsz%2Cwght%5D.ttf",
    "Montserrat": "https://raw.githubusercontent.com/google/fonts/main/ofl/montserrat/Montserrat%5Bwght%5D.ttf",
}
FONT_WEIGHTS = {"Inter": (400, 500, 700), "Montserrat": (600, 700)}

HOME_CARDS = (
    (
        "metal-inox-kesme-tasi",
        "metal-inox-kesme-tasi-card",
        "avif",
    ),
    (
        "355mm-metal-sabit-tezgah-kesme-diski",
        "355mm-metal-sabit-tezgah-kesme-diski-card",
        "avif",
    ),
    (
        "metal-inox-taslama-diski",
        "metal-inox-taslama-diski-kart-card",
        "webp",
    ),
    (
        "segmentli-standart-elmas-kesici",
        "segmentli-standart-elmas-kesici-kart-card",
        "webp",
    ),
    (
        "sds-plus-2-kesicili-beton-matkap-ucu",
        "sds-plus-2-kesicili-beton-matkap-ucu-card",
        "avif",
    ),
)


def site_characters() -> str:
    chars = set()
    extensions = {".html", ".json", ".js", ".css", ".txt", ".xml"}
    for path in ROOT.rglob("*"):
        if (
            not path.is_file()
            or path.suffix.lower() not in extensions
            or any(part in {".git", "node_modules", "agent-tools"} for part in path.parts)
        ):
            continue
        try:
            chars.update(path.read_text(encoding="utf-8"))
        except UnicodeDecodeError:
            continue
    chars.update("₺€₽©®™–—…“”‘’•→←✓")
    return "".join(sorted(chars))


def fetch(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "Abralion asset builder"})
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    with urllib.request.urlopen(request, timeout=90, context=context) as response:
        return response.read()


def build_fonts() -> None:
    FONT_DIR.mkdir(parents=True, exist_ok=True)
    text = site_characters()
    faces = []
    for family, url in FONT_SOURCES.items():
        source = fetch(url)
        for weight in FONT_WEIGHTS[family]:
            font = TTFont(io.BytesIO(source))
            axes = {"wght": weight}
            if "opsz" in {axis.axisTag for axis in font["fvar"].axes}:
                axes["opsz"] = 14
            instantiateVariableFont(font, axes, inplace=True)

            options = subset.Options()
            options.flavor = "woff2"
            options.layout_features = ["*"]
            options.name_IDs = ["*"]
            options.name_legacy = True
            options.name_languages = ["*"]
            subsetter = subset.Subsetter(options=options)
            subsetter.populate(text=text)
            subsetter.subset(font)

            filename = f"{family.lower()}-tr-{weight}-normal.woff2"
            output = FONT_DIR / filename
            font.flavor = "woff2"
            font.save(output)
            faces.append(
                "@font-face {\n"
                f"  font-family: '{family}';\n"
                "  font-style: normal;\n"
                f"  font-weight: {weight};\n"
                "  font-display: optional;\n"
                f"  src: url('../fonts/{filename}') format('woff2');\n"
                "}"
            )
            print(f"{output.relative_to(ROOT)}: {output.stat().st_size / 1024:.1f} KB")

    FONT_CSS.write_text(
        "/* Self-hosted Turkish subsets. font-display: optional prevents font-swap CLS. */\n\n"
        + "\n\n".join(faces)
        + "\n",
        encoding="utf-8",
    )
    for old in FONT_DIR.glob("*-latin*-normal.woff2"):
        old.unlink()


def save_responsive(source: Path, output: Path, image_format: str) -> None:
    with Image.open(source) as image:
        image.load()
        width = 440
        height = round(image.height * width / image.width)
        resized = image.resize((width, height), Image.Resampling.LANCZOS)
        if image_format == "avif":
            resized.save(output, "AVIF", quality=45)
        else:
            resized.save(output, "WEBP", quality=68, method=6)
    print(f"{output.relative_to(ROOT)}: {output.stat().st_size / 1024:.1f} KB")


def build_images() -> None:
    products = ROOT / "assets" / "images" / "products"
    for slug, stem, image_format in HOME_CARDS:
        directory = products / slug
        source = directory / f"{stem}.{image_format}"
        output = directory / f"{stem}-440.{image_format}"
        save_responsive(source, output, image_format)

    category_source = ROOT / "assets" / "images" / "home" / "kesici-taslar.jpg"
    category_output = ROOT / "assets" / "images" / "home" / "kesici-taslar-400.webp"
    with Image.open(category_source) as image:
        image.load()
        resized = image.resize((350, 350), Image.Resampling.LANCZOS)
        resized.save(category_output, "WEBP", quality=52, method=6)
    print(
        f"{category_output.relative_to(ROOT)}: "
        f"{category_output.stat().st_size / 1024:.1f} KB"
    )


if __name__ == "__main__":
    build_fonts()
    build_images()
