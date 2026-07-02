#!/usr/bin/env python3
"""Emit critical-home-lcp hero rules from tailwind.css (single source of truth)."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TAILWIND = ROOT / "assets" / "css" / "tailwind.css"


def tw_literal(selector: str) -> str:
    out = ["."]
    for ch in selector:
        if ch in ".[]":
            out.append("\\" + ch)
        elif ch == ":":
            out.append("\\:")
        else:
            out.append(ch)
    return "".join(out)


def rule(css: str, selector: str) -> str:
    needle = f"{tw_literal(selector)}{{"
    start = css.find(needle)
    if start < 0:
        raise KeyError(selector)
    start += len(needle)
    end = css.find("}", start)
    body = css[start:end]
    props = [p.strip() for p in body.split(";") if p.strip()]
    return ";".join(props)


def main() -> None:
    css = TAILWIND.read_text(encoding="utf-8")
    lines = [
        "/* hero typography — generated from tailwind.css; keep in sync via generate_critical_hero_css.py */",
        "#home-hero .home-hero__title{"
        + rule(css, "text-[2rem]")
        + ";"
        + rule(css, "leading-[1.1]")
        + ";font-weight:700;"
        + rule(css, "tracking-tight")
        + ";font-family:Montserrat,sans-serif;color:#fff;margin:0}",
        "@media(min-width:640px){#home-hero .home-hero__title{"
        + rule(css, "sm:text-headline-lg-mobile")
        + "}}",
        "@media(min-width:768px){#home-hero .home-hero__title{"
        + rule(css, "md:text-headline-lg")
        + "}}",
        "@media(min-width:1024px){#home-hero .home-hero__title{"
        + rule(css, "lg:text-headline-display")
        + "}}",
        "#home-hero .home-hero__subtitle{"
        + rule(css, "text-body-lg")
        + ";margin:0;max-width:42rem;font-family:Inter,sans-serif;color:#c8c6c5}",
        "#home-hero .home-hero__badge{margin:0;padding:0;background:transparent;display:flex;align-items:center;gap:.5rem}",
        "#home-hero .home-hero__badge-dot{width:8px;height:8px;background:#e2231a;border-radius:9999px;flex-shrink:0}",
        "#home-hero .home-hero__badge span:not(.home-hero__badge-dot){"
        + rule(css, "text-label-caps")
        + ";"
        + rule(css, "tracking-widest")
        + ";text-transform:uppercase;color:#ff756e;font-family:Inter,sans-serif}",
        "#home-hero .home-hero__accent,.home-hero__accent.text-abrasive-red{color:#e2231a}",
        "#home-hero .home-hero__actions{display:flex;flex-wrap:wrap;" + rule(css, "gap-4") + "}",
        "#home-hero .home-hero__actions a{display:inline-flex;align-items:center;"
        + rule(css, "px-8")
        + ";"
        + rule(css, "py-4")
        + ";"
        + rule(css, "text-label-caps")
        + ";text-transform:uppercase;border-radius:.25rem;font-family:Inter,sans-serif}",
        "#home-hero .home-hero__stats{display:flex;flex-wrap:wrap;"
        + rule(css, "gap-8")
        + ";border-top:1px solid rgba(255,255,255,.1);"
        + rule(css, "pt-8")
        + ";margin-top:0}",
        "#home-hero .home-hero__stat-value{display:block;"
        + rule(css, "text-headline-md")
        + ";color:#fff;font-family:Montserrat,sans-serif}",
        "#home-hero .home-hero__stat-label{display:block;"
        + rule(css, "text-technical-data")
        + ";text-transform:uppercase;color:#8e8e93;font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}",
        "#home-hero>.relative.z-10{position:relative;z-index:10;display:flex;flex:1;flex-direction:column;justify-content:center;width:100%;max-width:1280px;margin:0 auto;box-sizing:border-box;"
        + rule(css, "pt-28")
        + ";"
        + rule(css, "pb-8")
        + ";"
        + rule(css, "px-margin-mobile")
        + "}",
        "@media(min-width:768px){#home-hero>.relative.z-10{"
        + rule(css, "md:pt-32")
        + ";"
        + rule(css, "md:px-margin-desktop")
        + "}}",
        "@media(min-width:1024px){#home-hero>.relative.z-10{" + rule(css, "lg:pb-12") + "}}",
        ".home-hero__content{max-width:56rem;width:100%}",
        ".home-hero__content.max-w-4xl.space-y-8>*+*{margin-top:2rem}",
        "#home-hero .home-hero__btn-ghost{border:1px solid rgba(255,255,255,.2);color:#fff;background:transparent}",
    ]
    print("\n".join(lines))


if __name__ == "__main__":
    main()
