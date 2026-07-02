#!/usr/bin/env python3
"""Analyze orphan CSS vs live class usage."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from stage2_css_health import collect_html_js_classes, orphan_unique_rules, suspicious_coverage

used = collect_html_js_classes()
keywords = ("specs-table", "compare-table", "product-detail", "section")
matched = sorted(c for c in used if any(k in c for k in keywords))
print("HTML/JS classes (keyword):", len(matched))
for c in matched:
    print(" ", c)

print("\nSuspicious coverage:")
for k, v in suspicious_coverage().items():
    print(f"  {'OK' if v else 'MISSING'}: {k}")

orphan = orphan_unique_rules()
live = [r for r in orphan if set(re.findall(r"\.([a-zA-Z_][\w-]*)", r["selector"])) & used]
print(f"\nOrphan rules touching live classes: {len(live)}")
for r in live[:25]:
    print(f"  [{r['file']}] {r['selector']} | {r['property']}")
