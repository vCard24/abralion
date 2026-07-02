#!/usr/bin/env python3
"""JPEG içerikli .png dosyalarını .jpg'ye taşır ve HTML/JS/CSS referanslarını günceller."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
TEXT_GLOBS = ("*.html", "*.js", "*.css")
JPEG_MAGIC = b"\xff\xd8\xff"
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def detect_kind(path: Path) -> str:
    head = path.read_bytes()[:8]
    if head[:3] == JPEG_MAGIC:
        return "jpeg"
    if head[:8] == PNG_MAGIC:
        return "png"
    return "unknown"


def rel_posix(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def main() -> None:
    mappings: dict[str, str] = {}

    for png in sorted(ASSETS.rglob("*.png")):
        if detect_kind(png) != "jpeg":
            continue
        jpg = png.with_suffix(".jpg")
        old = rel_posix(png)
        new = rel_posix(jpg)
        if jpg.exists():
            png.unlink()
            print(f"silindi (jpg zaten var): {old}")
        else:
            png.rename(jpg)
            print(f"yeniden adlandırıldı: {old} -> {new}")
        mappings[old] = new

    if not mappings:
        print("Düzeltilecek JPEG-as-PNG dosyası yok.")
        return

    text_files: list[Path] = []
    for pattern in TEXT_GLOBS:
        text_files.extend(ROOT.rglob(pattern))
    text_files = sorted({p for p in text_files if "node_modules" not in p.parts})

    updated = 0
    for path in text_files:
        text = path.read_text(encoding="utf-8")
        new_text = text
        for old, new in mappings.items():
            new_text = new_text.replace(old, new)
            # Windows-style paths in some tooling
            new_text = new_text.replace(old.replace("/", "\\"), new.replace("/", "\\"))
        if new_text != text:
            path.write_text(new_text, encoding="utf-8", newline="\n")
            updated += 1
            print(f"güncellendi: {path.relative_to(ROOT)}")

    print(f"\n{len(mappings)} dosya düzeltildi, {updated} metin dosyası güncellendi.")


if __name__ == "__main__":
    main()
