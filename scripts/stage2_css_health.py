#!/usr/bin/env python3
"""Stage 2 CSS health: tinycss2 parse, duplicates, orphan diff, unused classes."""
from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

import tinycss2

ROOT = Path(__file__).resolve().parent.parent
CSS_DIR = ROOT / "assets" / "css"

BUNDLE_SOURCES = (
    "tailwind.css",
    "main.css",
    "components.css",
    "responsive.css",
    "site-extra.css",
)

ORPHAN_FILES = (
    "product-detail-page.css",
    "product-card-heroes.css",
    "fonts-selfhosted.css",
)

SKIP_PARSE = {"bundle.min.css", "tailwind-input.css"}

JS_CLASS_HINTS = (
    "className",
    "classList",
    "class=",
    "class:",
    "addClass",
    "toggle(",
    "innerHTML",
    "outerHTML",
    "querySelector",
)

SUSPICIOUS_SELECTORS = [
    ".specs-table",
    ".specs-table th",
    ".specs-table td",
    ".compare-table",
    ".compare-table-wrapper",
    ".compare-table th",
    ".product-detail-grid",
    ".product-detail-info",
    ".product-detail-image",
    ".product-detail-tab",
    ".product-detail-tabs-section",
    ".section",
    ".specs-table--stitch",
    ".page-product-detail .specs-table",
]


def source_css_files() -> list[Path]:
    files: list[Path] = []
    for name in sorted(CSS_DIR.glob("*.css")):
        if name.name in SKIP_PARSE:
            continue
        files.append(name)
    return files


def parse_stylesheet(path: Path) -> tuple[list, list]:
    text = path.read_text(encoding="utf-8")
    rules = tinycss2.parse_stylesheet(text, skip_comments=False, skip_whitespace=False)
    errors = [e for e in rules if isinstance(e, tinycss2.ast.ParseError)]
    warnings: list[str] = []
    for node in rules:
        if isinstance(node, tinycss2.ast.QualifiedRule):
            prelude = tinycss2.serialize(node.prelude).strip()
            if prelude.startswith("} ") or "} ." in prelude or prelude.startswith(".") and "@media" in text:
                pass
        if isinstance(node, tinycss2.ast.AtRule) and node.content is None and node.name in ("media", "keyframes"):
            warnings.append(f"empty @{node.name} block")
    return rules, errors


def strip_comments(css: str) -> str:
    return re.sub(r"/\*[^*]*\*+(?:[^/*][^*]*\*+)*/", "", css, flags=re.S)


def parse_rules(css: str) -> list[tuple[str, str, str]]:
    """Return list of (selector, body, property) for duplicate detection."""
    css = strip_comments(css)
    out: list[tuple[str, str, str]] = []
    for selector_part, body in re.findall(r"([^{}@][^{]*)\{([^{}]*)\}", css, flags=re.S):
        for raw in selector_part.split(","):
            sel = re.sub(r"\s+", " ", raw.strip())
            if not sel:
                continue
            for decl in body.split(";"):
                decl = decl.strip()
                if not decl or ":" not in decl:
                    continue
                prop, _, val = decl.partition(":")
                prop = prop.strip().lower()
                val = re.sub(r"\s+", " ", val.strip())
                if prop:
                    out.append((sel, prop, val))
    return out


def load_bundle_selector_set() -> set[str]:
    sels: set[str] = set()
    for name in BUNDLE_SOURCES:
        path = CSS_DIR / name
        if not path.is_file():
            continue
        css = strip_comments(path.read_text(encoding="utf-8"))
        for m in re.finditer(r"([^{}@][^{]*)\{", css, flags=re.S):
            selector_part = m.group(1)
            for raw in selector_part.split(","):
                sel = re.sub(r"\s+", " ", raw.strip())
                if sel:
                    sels.add(sel)
    return sels


def selector_in_bundle(selector: str, bundle: set[str]) -> bool:
    if selector in bundle:
        return True
    base = selector
    for prefix in (
        "body.dark-theme ",
        ".dark-theme ",
        "html.dark-theme ",
        "body:not(.page-noir-site) ",
        "body.dark-theme:not(.page-noir-site) ",
        ".page-product-detail ",
        ".page-product-detail-stitch ",
        ".page-compare ",
    ):
        if base.startswith(prefix):
            if base[len(prefix) :] in bundle:
                return True
    return False


def collect_html_js_classes() -> set[str]:
    classes: set[str] = set()
    class_attr = re.compile(r"""class\s*=\s*["']([^"']+)["']""", re.I)
    class_js = re.compile(r"""class(?:Name)?\s*[:=]\s*["'`]([^"'`]+)["'`]""")
    classList = re.compile(r"""classList\.(?:add|toggle|remove)\(\s*["']([^"']+)["']""")
    for pattern in ("*.html", "*.js"):
        for path in ROOT.rglob(pattern):
            if any(p in path.parts for p in ("node_modules", ".git", "vendor", "scripts/templates")):
                continue
            try:
                text = path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            for pat in (class_attr, class_js, classList):
                for m in pat.finditer(text):
                    for token in re.split(r"\s+", m.group(1).strip()):
                        token = token.split("{")[0].strip()
                        if token and re.match(r"^[a-zA-Z_][\w-]*$", token):
                            classes.add(token)
    return classes


def extract_class_tokens_from_selectors(selectors: set[str]) -> set[str]:
    tokens: set[str] = set()
    for sel in selectors:
        for m in re.finditer(r"\.([a-zA-Z_][\w-]*)", sel):
            tokens.add(m.group(1))
    return tokens


def orphan_unique_rules() -> list[dict]:
    bundle = load_bundle_selector_set()
    bundle_css = "\n".join(
        strip_comments((CSS_DIR / n).read_text(encoding="utf-8"))
        for n in BUNDLE_SOURCES
        if (CSS_DIR / n).is_file()
    )
    bundle_rules = parse_rules(bundle_css)
    bundle_triples = {(s, p, v) for s, p, v in bundle_rules}

    missing: list[dict] = []
    for orphan_name in ("product-detail-page.css", "product-card-heroes.css"):
        path = CSS_DIR / orphan_name
        if not path.is_file():
            continue
        for sel, prop, val in parse_rules(path.read_text(encoding="utf-8")):
            if (sel, prop, val) in bundle_triples:
                continue
            if selector_in_bundle(sel, bundle):
                continue
            missing.append({"file": orphan_name, "selector": sel, "property": prop, "value": val[:80]})
    return missing


def find_duplicates() -> dict[str, list[tuple[str, str]]]:
    """selector+property -> [(file, value), ...]"""
    acc: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for name in BUNDLE_SOURCES:
        path = CSS_DIR / name
        if not path.is_file():
            continue
        for sel, prop, val in parse_rules(path.read_text(encoding="utf-8")):
            key = f"{sel} | {prop}"
            acc[key].append((name, val))
    return {k: v for k, v in acc.items() if len(v) > 1}


def suspicious_coverage() -> dict[str, bool]:
    bundle = load_bundle_selector_set()
    return {sel: selector_in_bundle(sel, bundle) for sel in SUSPICIOUS_SELECTORS}


def main() -> int:
    report: dict = {}

    parse_results = {}
    total_errors = 0
    for path in source_css_files():
        rules, errors = parse_stylesheet(path)
        rel = path.relative_to(ROOT).as_posix()
        parse_results[rel] = {
            "rules": len([r for r in rules if isinstance(r, (tinycss2.ast.QualifiedRule, tinycss2.ast.AtRule))]),
            "errors": [str(e) for e in errors],
        }
        total_errors += len(errors)
    report["parse"] = parse_results

    dups = find_duplicates()
    exact_dupes = {k: v for k, v in dups.items() if len({val for _, val in v}) == 1}
    conflict_dupes = {k: v for k, v in dups.items() if len({val for _, val in v}) > 1}
    report["duplicates_exact_count"] = len(exact_dupes)
    report["duplicates_conflict_count"] = len(conflict_dupes)
    report["duplicates_conflict_sample"] = dict(list(conflict_dupes.items())[:30])

    report["suspicious_in_bundle"] = suspicious_coverage()
    report["orphan_unique_rules_count"] = len(orphan_unique_rules())
    report["orphan_unique_rules_sample"] = orphan_unique_rules()[:40]

    bundle_classes = extract_class_tokens_from_selectors(load_bundle_selector_set())
    used_classes = collect_html_js_classes()
    unused = sorted(bundle_classes - used_classes)
    report["bundle_class_tokens"] = len(bundle_classes)
    report["html_js_class_tokens"] = len(used_classes)
    report["possibly_unused_class_tokens"] = unused[:200]
    report["possibly_unused_count"] = len(unused)

    out_path = ROOT / "scripts" / "stage2_css_report.json"
    out_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"Parse errors: {total_errors}")
    for rel, info in parse_results.items():
        if info["errors"]:
            print(f"  {rel}: {len(info['errors'])} error(s)")
            for e in info["errors"][:3]:
                print(f"    {e}")
    print(f"Exact duplicate selector+property: {len(exact_dupes)}")
    print(f"Conflicting duplicate selector+property: {len(conflict_dupes)}")
    print(f"Suspicious selectors in bundle: {sum(report['suspicious_in_bundle'].values())}/{len(SUSPICIOUS_SELECTORS)}")
    print(f"Orphan unique rules (not in bundle): {report['orphan_unique_rules_count']}")
    print(f"Possibly unused class tokens (NOT deleted): {report['possibly_unused_count']}")
    print(f"Report: {out_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
