#!/usr/bin/env python3
"""PageSpeed-sensitive audit: fonts, images, cache bust, cache headers, animations."""
from __future__ import annotations

import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPORT = ROOT / "scripts" / "stage4_pagespeed_report.json"

FONT_BAD = re.compile(
    r"@font-face|font/ttf|\.ttf",
    re.I,
)
FONT_PRELOAD_BAD = re.compile(
    r'<link[^>]+rel=["\']preload["\'][^>]+as=["\']font["\'][^>]*>',
    re.I,
)
GOOGLE_FONTS = re.compile(
    r"fonts\.googleapis\.com/css2\?family=Inter.*Montserrat.*display=swap",
    re.I,
)
LOCAL_FONTS = re.compile(
    r"assets/css/fonts\.css\?v=[a-f0-9]+",
    re.I,
)
STALE_V = re.compile(r"\?v=20[0-9]{5}[a-z]?")
TRANSITION_ALL = re.compile(r"transition\s*:\s*all\b", re.I)
LAYOUT_ANIM = re.compile(
    r"transition[^;{]*(top|left|right|bottom|width|height|margin)[^;{]*;",
    re.I,
)


class ImgParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.imgs: list[dict] = []
        self._in_hero = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr = {k: (v or "") for k, v in attrs}
        if tag == "section" and attr.get("id") == "home-hero-wrap":
            self._in_hero = True
        if tag == "img":
            self.imgs.append(
                {
                    "src": attr.get("src", ""),
                    "width": attr.get("width", ""),
                    "height": attr.get("height", ""),
                    "loading": attr.get("loading", ""),
                    "fetchpriority": attr.get("fetchpriority", ""),
                    "in_hero": self._in_hero,
                    "line": self.getpos()[0],
                }
            )

    def handle_endtag(self, tag: str) -> None:
        if tag == "section" and self._in_hero:
            self._in_hero = False


def html_files() -> list[Path]:
    out: list[Path] = []
    for path in sorted(ROOT.rglob("*.html")):
        if "node_modules" in path.parts:
            continue
        rel = path.relative_to(ROOT)
        if rel.parts[0] == "scripts":
            if "templates" not in rel.parts:
                continue
            if rel.name == "product-detail-main-stitch.html":
                continue
        out.append(path)
    return out


def audit_fonts(files: list[Path]) -> dict:
    issues: list[str] = []
    ok_pages = 0
    for path in files:
        text = path.read_text(encoding="utf-8")
        rel = str(path.relative_to(ROOT)).replace("\\", "/")
        if FONT_BAD.search(text):
            issues.append(f"{rel}: inline TTF / @font-face detected")
        for m in FONT_PRELOAD_BAD.finditer(text):
            if "woff2" not in m.group(0):
                issues.append(f"{rel}: non-woff2 font preload")
                break
        if GOOGLE_FONTS.search(text):
            issues.append(f"{rel}: still uses Google Fonts CDN")
        elif not LOCAL_FONTS.search(text):
            issues.append(f"{rel}: missing self-hosted fonts.css link")
        else:
            ok_pages += 1
    return {"ok_pages": ok_pages, "issues": issues}


def audit_versions(files: list[Path]) -> list[str]:
    issues: list[str] = []
    for path in files:
        text = path.read_text(encoding="utf-8")
        rel = str(path.relative_to(ROOT)).replace("\\", "/")
        for m in STALE_V.finditer(text):
            issues.append(f"{rel}: stale ?v= {m.group(0)}")
        for m in re.finditer(r'(?:\.\./)?assets/(?:css|js)/[^"\s>?#]+\.(?:css|js)(?!\?v=)', text):
            ref = m.group(0)
            if "vendor/" in ref:
                continue
            issues.append(f"{rel}: unversioned asset {ref}")
    return issues


def audit_images(files: list[Path]) -> dict:
    missing_dims: list[str] = []
    lazy_hero: list[str] = []
    hero_no_priority: list[str] = []
    below_fold_eager: list[str] = []

    for path in files:
        rel = str(path.relative_to(ROOT)).replace("\\", "/")
        parser = ImgParser()
        try:
            parser.feed(path.read_text(encoding="utf-8"))
        except Exception as exc:
            missing_dims.append(f"{rel}: parse error {exc}")
            continue
        for img in parser.imgs:
            src = img["src"]
            if src.startswith("http://") or src.startswith("https://") or src.startswith("data:"):
                continue
            if not img["width"] or not img["height"]:
                missing_dims.append(f"{rel}:{img['line']} {img['src'] or '(no src)'}")
            if img["in_hero"]:
                if img["loading"] == "lazy":
                    lazy_hero.append(f"{rel}:{img['line']}")
                if img["fetchpriority"] != "high":
                    hero_no_priority.append(f"{rel}:{img['line']}")
            elif img["loading"] not in ("lazy", ""):
                if img["loading"] == "eager":
                    below_fold_eager.append(f"{rel}:{img['line']} {img['src']}")

    return {
        "missing_dimensions": missing_dims,
        "hero_lazy": lazy_hero,
        "hero_missing_fetchpriority": hero_no_priority,
        "below_fold_eager": below_fold_eager,
    }


def audit_htaccess() -> dict:
    path = ROOT / ".htaccess"
    text = path.read_text(encoding="utf-8") if path.is_file() else ""
    return {
        "exists": path.is_file(),
        "css_immutable": "max-age=31536000, immutable" in text and ".css" in text,
        "js_immutable": "(js|mjs)" in text and "max-age=31536000, immutable" in text,
        "html_no_cache": "text/html" in text and ("no-cache" in text or "0 seconds" in text),
        "woff2_cache": "font/woff2" in text,
    }


def audit_css_animations() -> dict:
    sources = [
        ROOT / "assets/css/main.css",
        ROOT / "assets/css/components.css",
        ROOT / "assets/css/responsive.css",
        ROOT / "assets/css/site-extra.css",
    ]
    transition_all: list[str] = []
    layout_transitions: list[str] = []
    for path in sources:
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        rel = path.name
        for i, line in enumerate(text.splitlines(), 1):
            if TRANSITION_ALL.search(line):
                transition_all.append(f"{rel}:{i}")
            if LAYOUT_ANIM.search(line):
                layout_transitions.append(f"{rel}:{i}: {line.strip()[:100]}")
    return {
        "transition_all": transition_all,
        "layout_property_transitions": layout_transitions,
    }


def audit_critical_hero() -> dict:
    index = ROOT / "index.html"
    if not index.is_file():
        return {"ok": False, "error": "index.html missing"}
    text = index.read_text(encoding="utf-8")
    if FONT_BAD.search(text):
        return {"ok": False, "error": "critical block contains TTF @font-face"}
    m = re.search(r'<style id="critical-home-lcp">(.*?)</style>', text, re.S)
    if not m:
        return {"ok": False, "error": "critical-home-lcp block missing"}
    block = m.group(1)
    required = [
        "#home-hero .home-hero__title",
        "@media(min-width:1024px)",
        "footer.footer a{color:#e2e2e2",
        "min-height:min(90vh,920px)",
    ]
    missing = [r for r in required if r not in block]
    return {"ok": not missing, "missing_rules": missing, "bytes": len(block)}


def main() -> int:
    files = html_files()
    report = {
        "fonts": audit_fonts(files),
        "versions": audit_versions(files),
        "images": audit_images(files),
        "htaccess": audit_htaccess(),
        "css_animations": audit_css_animations(),
        "critical_hero": audit_critical_hero(),
    }
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    issues = 0
    issues += len(report["fonts"]["issues"])
    issues += len(report["versions"])
    for key in report["images"]:
        issues += len(report["images"][key])
    if not report["critical_hero"].get("ok"):
        issues += 1
    issues += len(report["css_animations"]["transition_all"])

    print(f"Wrote {REPORT.relative_to(ROOT)}")
    print(f"Font pages OK: {report['fonts']['ok_pages']}/{len(files)}")
    print(f"Open issues: {issues}")
    if issues:
        for item in report["fonts"]["issues"][:5]:
            print(f"  font: {item}")
        for item in report["versions"][:5]:
            print(f"  version: {item}")
        for item in report["images"]["missing_dimensions"][:5]:
            print(f"  img: {item}")
        for item in report["css_animations"]["transition_all"][:5]:
            print(f"  css: transition:all @ {item}")
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
