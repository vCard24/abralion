#!/usr/bin/env python3
"""Find structural CSS properties lost when selectors were reduced to theme overrides."""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BEFORE = "af30302"
FILES = (
    "assets/css/compare.css",
    "assets/css/components.css",
    "assets/css/main.css",
    "assets/css/product-card-heroes.css",
    "assets/css/product-detail-page.css",
    "assets/css/quote-form.css",
    "assets/css/responsive.css",
    "assets/css/site-extra.css",
)

STRUCTURAL = {
    "width",
    "height",
    "display",
    "flex-shrink",
    "min-height",
    "max-height",
    "padding",
    "padding-top",
    "padding-bottom",
    "grid-template-columns",
    "gap",
    "overflow",
    "border-radius",
    "align-items",
    "justify-content",
    "flex-direction",
    "position",
    "box-sizing",
    "font-size",
    "line-height",
    "border",
    "text-decoration",
}


def git_show(commit: str, path: str) -> str:
    proc = subprocess.run(
        ["git", "show", f"{commit}:{path}"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        cwd=ROOT,
    )
    return proc.stdout if proc.returncode == 0 else ""


def parse_rules(css: str) -> dict[str, str]:
    css = re.sub(r"/\*[^*]*\*+(?:[^/*][^*]*\*+)*/", "", css, flags=re.S)
    rules: dict[str, str] = {}
    for selector_part, body in re.findall(r"([^{}@][^{]*)\{([^{}]*)\}", css, flags=re.S):
        for raw in selector_part.split(","):
            sel = re.sub(r"\s+", " ", raw.strip())
            if sel:
                rules.setdefault(sel, body.strip())
    return rules


def props(body: str) -> set[str]:
    return {line.split(":", 1)[0].strip().lower() for line in body.split(";") if ":" in line}


def main() -> None:
    total = 0
    for rel in FILES:
        before = parse_rules(git_show(BEFORE, rel))
        path = ROOT / rel
        if not path.is_file():
            print(f"MISSING FILE {rel}")
            continue
        now = parse_rules(path.read_text(encoding="utf-8"))
        lost: list[tuple[str, list[str]]] = []
        for sel, body in before.items():
            if sel not in now:
                continue
            missing = sorted((props(body) - props(now[sel])) & STRUCTURAL)
            if missing:
                lost.append((sel, missing))
        if not lost:
            continue
        print(f"\n{rel}: {len(lost)} selectors with lost properties")
        for sel, missing in lost:
            print(f"  {sel} -> {', '.join(missing)}")
        total += len(lost)
    print(f"\nTOTAL property-loss selectors: {total}")


if __name__ == "__main__":
    main()
