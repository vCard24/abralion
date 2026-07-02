#!/usr/bin/env python3
"""Stage 2: merge dark-theme.css + noir-migration.css into base CSS files."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CSS = ROOT / "assets" / "css"

FILES = {
    "main": CSS / "main.css",
    "components": CSS / "components.css",
    "responsive": CSS / "responsive.css",
    "site_extra": CSS / "site-extra.css",
}
DARK_THEME = CSS / "dark-theme.css"
NOIR = CSS / "noir-migration.css"
BUILD = ROOT / "scripts" / "build_css.py"

DARK_PREFIXES = (
    "html.dark-theme body ",
    "html.dark-theme ",
    "html.dark body ",
)


def strip_comments(css: str) -> str:
    return re.sub(r"/\*[^*]*\*+(?:[^/*][^*]*\*+)*/", "", css)


def split_rules(css: str) -> list[tuple[str, str]]:
    rules: list[tuple[str, str]] = []
    css = strip_comments(css)
    i = 0
    length = len(css)
    while i < length:
        while i < length and css[i].isspace():
            i += 1
        if i >= length:
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
        selector = css[i:brace].strip()
        depth = 1
        j = brace + 1
        while j < length and depth:
            if css[j] == "{":
                depth += 1
            elif css[j] == "}":
                depth -= 1
            j += 1
        body = css[brace + 1 : j - 1].strip()
        rules.append((selector, body))
        i = j
    return rules


def normalize_selector(selector: str) -> str:
    s = selector.strip()
    if s.startswith("@"):
        return s
    for prefix in DARK_PREFIXES:
        if s.startswith(prefix):
            s = s[len(prefix) :]
    return re.sub(r"\s+", " ", s).strip()


def normalize_body(body: str) -> str:
    body = re.sub(r"\s*!important\b", "", body)
    return re.sub(r"\s+", " ", body).strip()


def extract_dark_variables(css: str) -> str:
    marker = "html.dark-theme body {"
    start = css.find(marker)
    if start == -1:
        return ""
    brace = css.find("{", start)
    depth = 1
    j = brace + 1
    while j < len(css) and depth:
        if css[j] == "{":
            depth += 1
        elif css[j] == "}":
            depth -= 1
        j += 1
    inner = css[brace + 1 : j - 1]
    lines = []
    for ln in inner.splitlines():
        ln = ln.strip()
        if not ln or ln.startswith("/*"):
            continue
        prop = ln.split(":")[0].strip()
        if prop in {"background", "color"}:
            continue
        lines.append(ln)
    return ":root {\n  " + "\n  ".join(lines) + "\n}\n"


def replace_root_block(main_css: str, new_root: str) -> str:
    pattern = re.compile(r":root\s*\{[^}]*\}", re.DOTALL)
    if pattern.search(main_css):
        return pattern.sub(new_root.strip(), main_css, count=1)
    return new_root + "\n\n" + main_css


def patch_main_body(main_css: str) -> str:
    return re.sub(
        r"body\s*\{[^}]*\}",
        (
            "body {\n"
            "  font-family: var(--font-family);\n"
            "  line-height: var(--line-height);\n"
            "  color: var(--color-text-primary, #e4e4e7);\n"
            "  background: var(--gradient-base, linear-gradient(180deg, #1f1f20 0%, #1a1a1b 100%));\n"
            "}"
        ),
        main_css,
        count=1,
    )


def merge_overlay(
    buckets: dict[str, list[tuple[str, str]]],
    overlay: list[tuple[str, str]],
    default_bucket: str,
) -> None:
    lookup: dict[str, tuple[str, int]] = {}
    for bucket, rules in buckets.items():
        for idx, (sel, _) in enumerate(rules):
            lookup[normalize_selector(sel)] = (bucket, idx)

    for selector, body in overlay:
        norm_sel = normalize_selector(selector)
        norm_body = normalize_body(body)
        if norm_sel in {"html.dark-theme body", "body"} and "--color-primary" in body:
            continue
        if not norm_body and not norm_sel.startswith("@"):
            continue
        if norm_sel in lookup:
            bucket, idx = lookup[norm_sel]
            buckets[bucket][idx] = (norm_sel, norm_body)
        else:
            buckets[default_bucket].append((norm_sel, norm_body))
            lookup[norm_sel] = (default_bucket, len(buckets[default_bucket]) - 1)


def rules_to_css(rules: list[tuple[str, str]]) -> str:
    chunks: list[str] = []
    for selector, body in rules:
        if selector.startswith("@"):
            chunks.append(selector if not body else f"{selector} {{ {body} }}")
        elif body:
            decls = body if ";" not in body else body.replace("; ", ";\n  ")
            chunks.append(f"{selector} {{\n  {decls}\n}}")
        else:
            chunks.append(selector)
    return "\n\n".join(chunks) + "\n"


def remove_file_from_build(name: str) -> None:
    text = BUILD.read_text(encoding="utf-8")
    text = re.sub(rf'\s*"{re.escape(name)}",?\n', "\n", text)
    BUILD.write_text(text, encoding="utf-8")


def main() -> None:
    dark_raw = DARK_THEME.read_text(encoding="utf-8")
    noir_raw = NOIR.read_text(encoding="utf-8")

    buckets: dict[str, list[tuple[str, str]]] = {}
    for key, path in FILES.items():
        raw = path.read_text(encoding="utf-8")
        if key == "main":
            raw = replace_root_block(raw, extract_dark_variables(dark_raw))
            raw = patch_main_body(raw)
        buckets[key] = split_rules(raw)

    merge_overlay(buckets, split_rules(dark_raw), "components")
    merge_overlay(buckets, split_rules(noir_raw), "site_extra")

    for key, path in FILES.items():
        path.write_text(rules_to_css(buckets[key]), encoding="utf-8")

    DARK_THEME.unlink()
    NOIR.unlink()
    remove_file_from_build("dark-theme.css")
    remove_file_from_build("noir-migration.css")

    total = sum(path.stat().st_size for path in FILES.values())
    total += (CSS / "tailwind.css").stat().st_size
    print(f"Deleted dark-theme.css ({len(dark_raw)} B) and noir-migration.css ({len(noir_raw)} B)")
    print(f"5-file source total: {total / 1024:.1f} KB")


if __name__ == "__main__":
    main()
