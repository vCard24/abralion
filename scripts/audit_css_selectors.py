#!/usr/bin/env python3
"""Compare CSS selectors before Stage 2 merge vs current source CSS files."""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_BEFORE = "af30302"

# Hand-authored layers only (tailwind.css is generated from config).
BEFORE_CSS_PATHS = (
    "assets/css/compare.css",
    "assets/css/components.css",
    "assets/css/dark-theme.css",
    "assets/css/gallery-lightbox.css",
    "assets/css/main.css",
    "assets/css/noir-migration.css",
    "assets/css/product-card-heroes.css",
    "assets/css/product-detail-page.css",
    "assets/css/quote-form.css",
    "assets/css/responsive.css",
    "assets/css/site-extra.css",
)

CURRENT_SKIP = {"bundle.min.css", "tailwind.css", "tailwind-input.css", "fonts-selfhosted.css"}

INTENTIONAL_PREFIXES = (
    ".light-theme",
    "html:not(.dark-theme)",
    "body:not(.dark-theme)",
)

INTENTIONAL_KEYWORDS = (
    "prefers-color-scheme: light",
    "theme-toggle",
    "theme-init",
)

STRUCTURAL_HINTS = (
    "width:",
    "height:",
    "display:",
    "grid-template",
    "position:",
    "padding:",
    "margin:",
    "min-height:",
    "max-width:",
    "overflow:",
    "border-radius:",
    "gap:",
    "flex-shrink:",
    "align-items:",
    "justify-content:",
)


def git_show(commit: str, path: str) -> str:
    proc = subprocess.run(
        ["git", "show", f"{commit}:{path}"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        cwd=ROOT,
    )
    return proc.stdout if proc.returncode == 0 else ""


def strip_comments(css: str) -> str:
    return re.sub(r"/\*[^*]*\*+(?:[^/*][^*]*\*+)*/", "", css, flags=re.S)


def normalize_selector(selector: str) -> str:
    return re.sub(r"\s+", " ", selector.strip())


def parse_rules(css: str) -> dict[str, str]:
    css = strip_comments(css)
    rules: dict[str, str] = {}
    for selector_part, body in re.findall(r"([^{}@][^{]*)\{([^{}]*)\}", css, flags=re.S):
        for raw in selector_part.split(","):
            sel = normalize_selector(raw)
            if sel and sel not in rules:
                rules[sel] = body.strip()
    return rules


def load_before_rules(commit: str) -> dict[str, str]:
    merged: dict[str, str] = {}
    for rel in BEFORE_CSS_PATHS:
        for sel, body in parse_rules(git_show(commit, rel)).items():
            merged.setdefault(sel, body)
    return merged


def load_current_rules() -> dict[str, str]:
    merged: dict[str, str] = {}
    for path in sorted((ROOT / "assets" / "css").glob("*.css")):
        if path.name in CURRENT_SKIP:
            continue
        for sel, body in parse_rules(path.read_text(encoding="utf-8")).items():
            merged.setdefault(sel, body)
    return merged


def selector_variants(selector: str) -> set[str]:
    variants = {selector}
    for prefix in (
        "body.dark-theme ",
        ".dark-theme ",
        "html.dark-theme ",
        "body:not(.page-noir-site) ",
        "body.dark-theme:not(.page-noir-site) ",
    ):
        if selector.startswith(prefix):
            variants.add(selector[len(prefix) :])
    return variants


def exists_in_current(selector: str, current: set[str]) -> bool:
    if selector in current:
        return True
    return any(v in current for v in selector_variants(selector))


def classify_missing(selector: str, body: str) -> str:
    low = f"{selector} {body}".lower()
    for prefix in INTENTIONAL_PREFIXES:
        if selector.startswith(prefix) or prefix in selector:
            return "intentional_light_theme"
    for kw in INTENTIONAL_KEYWORDS:
        if kw in low:
            return "intentional_theme_infra"
    if selector in {":root", "html", "body"}:
        return "intentional_global"
    if any(h in body for h in STRUCTURAL_HINTS):
        return "suspect_structural"
    if re.search(r"(color|background|border-color|box-shadow)\s*:", body):
        return "suspect_cosmetic"
    return "suspect_other"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--before", default=DEFAULT_BEFORE)
    parser.add_argument("--all", action="store_true", help="Include intentional omissions in listing")
    args = parser.parse_args()

    before = load_before_rules(args.before)
    current_rules = load_current_rules()
    current_selectors = set(current_rules)

    missing = [
        (sel, body, classify_missing(sel, body))
        for sel, body in sorted(before.items())
        if not exists_in_current(sel, current_selectors)
    ]

    counts: dict[str, int] = {}
    for _, _, kind in missing:
        counts[kind] = counts.get(kind, 0) + 1

    print(f"Before commit: {args.before}")
    print(f"Selectors before merge: {len(before)}")
    print(f"Selectors in current sources: {len(current_selectors)}")
    print(f"Missing from current sources: {len(missing)}")
    for kind in sorted(counts):
        print(f"  {kind}: {counts[kind]}")

    print("\n--- Missing selectors (suspect / review) ---")
    for sel, body, kind in missing:
        if kind.startswith("intentional") and not args.all:
            continue
        preview = re.sub(r"\s+", " ", body)[:110]
        print(f"[{kind}] {sel} {{ {preview} }}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
