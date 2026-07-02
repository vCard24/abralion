# -*- coding: utf-8 -*-
"""Aşama 5: HTML tutarlılığı ve temel a11y denetimi."""
from __future__ import annotations

import json
import re
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REPORT = ROOT / "scripts" / "stage5_html_report.json"

SKIP_PREFIXES = (
    "scripts/includes/",
    "node_modules/",
)
SKIP_FILES = {
    "scripts/templates/product-detail-main-stitch.html",
}


class PageScan(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.lang: str | None = None
        self.title: str = ""
        self.in_title = False
        self.meta: dict[str, str] = {}
        self.og: dict[str, str] = {}
        self.canonical: str | None = None
        self.headings: list[str] = []
        self.imgs_missing_alt: list[str] = []
        self.skip_link = False
        self.has_main = False
        self.unlabeled_inputs: list[str] = []
        self.nav_aria: list[str] = []
        self._label_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        a = {k: v for k, v in attrs if v is not None}
        tl = tag.lower()
        if tl == "html":
            self.lang = a.get("lang")
        if tl == "label":
            self._label_depth += 1
        if tl == "title":
            self.in_title = True
        if tl == "meta":
            name = a.get("name", "").lower()
            prop = a.get("property", "").lower()
            content = a.get("content", "")
            if name:
                self.meta[name] = content
            if prop.startswith("og:"):
                self.og[prop] = content
        if tl == "link" and a.get("rel") == "canonical":
            self.canonical = a.get("href")
        if tl in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            self.headings.append(tl)
        if tl == "img" and "alt" not in a:
            self.imgs_missing_alt.append(a.get("src", "")[:80])
        if tl == "a" and a.get("href", "").startswith("#main"):
            self.skip_link = True
        if tl == "main":
            self.has_main = True
        if tl == "nav" and "aria-label" in a:
            self.nav_aria.append(a["aria-label"])
        if tl == "input":
            typ = a.get("type", "text")
            if typ in {"hidden", "submit", "button"}:
                return
            if self._label_depth > 0:
                return
            if a.get("aria-label") or a.get("aria-labelledby"):
                return
            if a.get("id"):
                return
            self.unlabeled_inputs.append(a.get("name") or a.get("placeholder") or "?")

    def handle_endtag(self, tag: str) -> None:
        tl = tag.lower()
        if tl == "title":
            self.in_title = False
        if tl == "label" and self._label_depth:
            self._label_depth -= 1

    def handle_data(self, data: str) -> None:
        if self.in_title:
            self.title += data


def iter_html_files() -> list[Path]:
    out: list[Path] = []
    for path in sorted(ROOT.rglob("*.html")):
        rel = path.relative_to(ROOT).as_posix()
        if rel in SKIP_FILES:
            continue
        if any(rel.startswith(p) for p in SKIP_PREFIXES):
            continue
        out.append(path)
    return out


def audit_page(path: Path) -> list[str]:
    rel = path.relative_to(ROOT).as_posix()
    is_template = rel.startswith("scripts/templates/")
    text = path.read_text(encoding="utf-8")
    scan = PageScan()
    scan.feed(text)

    issues: list[str] = []
    if scan.lang != "tr":
        issues.append(f'lang="{scan.lang}" (beklenen tr)')
    if not scan.title.strip():
        issues.append("title eksik")
    if not scan.meta.get("description"):
        issues.append("meta description eksik")
    for key in ("og:title", "og:description", "og:image", "og:url"):
        if not scan.og.get(key):
            issues.append(f"{key} eksik")
    if not scan.meta.get("viewport"):
        issues.append("viewport meta eksik")
    if not is_template and not scan.canonical:
        issues.append("canonical eksik")
    h1_count = scan.headings.count("h1")
    if h1_count == 0:
        issues.append("h1 yok")
    elif h1_count > 1:
        issues.append(f"{h1_count} adet h1")
    if not is_template:
        if not scan.skip_link:
            issues.append("skip link (#main-content) yok")
        if not scan.has_main:
            issues.append("<main> yok")
    if scan.imgs_missing_alt:
        issues.append(f"{len(scan.imgs_missing_alt)} img alt attribute yok")
    if scan.unlabeled_inputs:
        preview = ", ".join(scan.unlabeled_inputs[:4])
        issues.append(f"label/aria eksik input: {preview}")

    # Heading order: flag level skips in main content (ignore footer h2 after h1)
    levels = [int(h[1]) for h in scan.headings]
    for i in range(1, len(levels)):
        if levels[i] > levels[i - 1] + 1:
            issues.append(
                f"heading atlama: {scan.headings[i - 1]} -> {scan.headings[i]}"
            )
            break

    return issues


def main() -> None:
    files = iter_html_files()
    report: dict[str, list[str]] = {}
    for path in files:
        rel = path.relative_to(ROOT).as_posix()
        issues = audit_page(path)
        if issues:
            report[rel] = issues

    REPORT.write_text(
        json.dumps({"files_scanned": len(files), "issues": report}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"Taranan: {len(files)} HTML")
    print(f"Sorunlu: {len(report)} dosya\n")
    for rel in sorted(report):
        print(rel)
        for item in report[rel]:
            print(f"  - {item}")
    print(f"\nRapor: {REPORT.relative_to(ROOT).as_posix()}")


if __name__ == "__main__":
    main()
