#!/usr/bin/env python3
"""Strip obsolete html.dark-theme prefixes; drop duplicate selector rules."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CSS = ROOT / "assets" / "css"
TARGETS = ("components.css", "responsive.css", "site-extra.css", "main.css")

PREFIXES = (
    "html.dark-theme body ",
    "html.dark-theme ",
)


def strip_prefix(selector: str) -> str:
    s = selector.strip()
    if s.startswith("@"):
        return s
    for p in PREFIXES:
        if s.startswith(p):
            s = s[len(p) :]
    return re.sub(r"\s+", " ", s).strip()


def strip_selector_list(selector: str) -> str:
    if selector.startswith("@"):
        return selector
    parts: list[str] = []
    seen: set[str] = set()
    for part in selector.split(","):
        norm = strip_prefix(part)
        if norm and norm not in seen:
            seen.add(norm)
            parts.append(norm)
    return ", ".join(parts)


def split_rules(css: str) -> list[tuple[str, str]]:
    rules: list[tuple[str, str]] = []
    css = re.sub(r"/\*[^*]*\*+(?:[^/*][^*]*\*+)*/", "", css)
    i, n = 0, len(css)
    while i < n:
        while i < n and css[i].isspace():
            i += 1
        if i >= n:
            break
        if css.startswith("@", i):
            semi = css.find(";", i)
            if semi == -1:
                break
            rules.append((css[i : semi + 1].strip(), ""))
            i = semi + 1
            continue
        brace = css.find("{", i)
        if brace == -1:
            break
        sel = css[i:brace].strip()
        depth, j = 1, brace + 1
        while j < n and depth:
            depth += 1 if css[j] == "{" else (-1 if css[j] == "}" else 0)
            j += 1
        rules.append((sel, css[brace + 1 : j - 1].strip()))
        i = j
    return rules


def dedupe(rules: list[tuple[str, str]]) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []
    idx: dict[str, int] = {}
    for sel, body in rules:
        norm = strip_selector_list(sel)
        if norm in idx:
            out[idx[norm]] = (norm, body)
        else:
            idx[norm] = len(out)
            out.append((norm, body))
    return out


def to_css(rules: list[tuple[str, str]]) -> str:
    parts = []
    for sel, body in rules:
        if sel.startswith("@"):
            parts.append(sel if not body else f"{sel} {{ {body} }}")
        else:
            parts.append(f"{sel} {{\n  {body.replace('; ', ';\n  ')}\n}}")
    return "\n\n".join(parts) + "\n"


def main() -> None:
    for name in TARGETS:
        path = CSS / name
        raw = path.read_text(encoding="utf-8")
        cleaned = to_css(dedupe(split_rules(raw)))
        path.write_text(cleaned, encoding="utf-8")
        print(f"{name}: {path.stat().st_size / 1024:.1f} KB")


if __name__ == "__main__":
    main()
