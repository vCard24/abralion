#!/usr/bin/env python3
"""Restore base CSS properties lost when dark overrides replaced full rules."""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BEFORE = "af30302"
TARGET_FILES = (
    "assets/css/compare.css",
    "assets/css/components.css",
    "assets/css/main.css",
    "assets/css/product-card-heroes.css",
    "assets/css/product-detail-page.css",
    "assets/css/quote-form.css",
    "assets/css/responsive.css",
    "assets/css/site-extra.css",
)

SKIP_RESTORE_SELECTORS = {
    ".material-symbols-outlined",
    ".page-quote .quote-prefill-banner .material-symbols-outlined",
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


def strip_comments(css: str) -> str:
    return re.sub(r"/\*[^*]*\*+(?:[^/*][^*]*\*+)*/", "", css, flags=re.S)


def normalize_selector(selector: str) -> str:
    return re.sub(r"\s+", " ", selector.strip())


def parse_declarations(body: str) -> list[tuple[str, str]]:
    decls: list[tuple[str, str]] = []
    for chunk in body.split(";"):
        chunk = chunk.strip()
        if not chunk or ":" not in chunk:
            continue
        prop, val = chunk.split(":", 1)
        decls.append((prop.strip(), val.strip()))
    return decls


def format_declarations(decls: list[tuple[str, str]]) -> str:
    return "\n".join(f"  {prop}: {val};" for prop, val in decls)


def merge_bodies(before_body: str, now_body: str) -> str:
    merged: dict[str, str] = {}
    for prop, val in parse_declarations(before_body):
        merged[prop] = val
    for prop, val in parse_declarations(now_body):
        merged[prop] = val
    return format_declarations(list(merged.items()))


def parse_top_level_rules(css: str) -> dict[str, str]:
    css = strip_comments(css)
    rules: dict[str, str] = {}
    for selector_part, body in re.findall(r"([^{}@][^{]*)\{([^{}]*)\}", css, flags=re.S):
        for raw in selector_part.split(","):
            sel = normalize_selector(raw)
            if sel:
                rules[sel] = body.strip()
    return rules


def replace_rule_body(css: str, selector: str, new_body: str) -> tuple[str, bool]:
    pattern = rf"({re.escape(selector)}\s*)\{{[^{{}}]*\}}"
    repl = rf"\1{{\n{new_body}\n}}"
    new_css, count = re.subn(pattern, repl, css, count=1, flags=re.S)
    return new_css, count > 0


def restore_file(rel: str) -> tuple[int, int]:
    before_rules = parse_top_level_rules(git_show(BEFORE, rel))
    path = ROOT / rel
    css = path.read_text(encoding="utf-8")
    now_rules = parse_top_level_rules(css)
    merged_count = 0
    added_count = 0

    for sel, now_body in now_rules.items():
        if sel not in before_rules:
            continue
        merged = merge_bodies(before_rules[sel], now_body)
        if merged == format_declarations(parse_declarations(now_body)):
            continue
        css, ok = replace_rule_body(css, sel, merged)
        if ok:
            merged_count += 1

    for sel, before_body in before_rules.items():
        if sel in SKIP_RESTORE_SELECTORS or sel in now_rules:
            continue
        if sel.startswith(("html.dark-theme ", "body.dark-theme ")):
            continue
        css += (
            f"\n\n/* restored base rule */\n{sel} {{\n"
            f"{format_declarations(parse_declarations(before_body))}\n}}\n"
        )
        added_count += 1

    if merged_count or added_count:
        path.write_text(css, encoding="utf-8")
    return merged_count, added_count


def main() -> int:
    files = sys.argv[1:] if len(sys.argv) > 1 else list(TARGET_FILES)
    total_merged = 0
    total_added = 0
    for rel in files:
        if not (ROOT / rel).is_file():
            continue
        merged, added = restore_file(rel)
        print(f"{rel}: merged {merged}, added {added}")
        total_merged += merged
        total_added += added
    print(f"Done. merged={total_merged}, added={total_added}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
