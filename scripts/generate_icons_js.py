#!/usr/bin/env python3
"""Generate assets/js/icons.js from scripts/icon_paths.py."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
from icon_paths import ICON_PATHS  # noqa: E402

OUT = ROOT / "assets" / "js" / "icons.js"


def main() -> None:
    paths_json = json.dumps(ICON_PATHS, indent=2, ensure_ascii=False)
    content = f"""/* Inline Material-style icons — no external font */
const ICON_PATHS = {paths_json};

function iconSvg(name, extraClass = '') {{
  const path = ICON_PATHS[name];
  if (!path) return '';
  const cls = extraClass ? ` class="${{extraClass}} icon-svg"` : ' class="icon-svg"';
  return (
    `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="1em" height="1em" fill="currentColor" aria-hidden="true"${{cls}}>` +
    `<path d="${{path}}"/></svg>`
  );
}}

window.AbralionIcons = {{ ICON_PATHS, iconSvg }};
"""
    OUT.write_text(content, encoding="utf-8")
    print(f"Wrote {OUT.relative_to(ROOT)} ({len(ICON_PATHS)} icons)")


if __name__ == "__main__":
    main()
