#!/usr/bin/env python3
"""Add cache-bust query strings to site.js and components.css across HTML files."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ASSET_VER = "20260605"
CSS_VER = "20260603"
PRODUCT_IMAGE_UTILS_VER = "20260610"


def patch(content: str) -> tuple[str, bool]:
    orig = content
    if "product-image-utils.js" not in content:
        content = re.sub(
            r'(<script defer src="(\.\./)?assets/js/site\.js(?:\?v=[^"]+)?"></script>)',
            lambda m: (
                f'<script defer src="{m.group(2) or ""}assets/js/product-image-utils.js?v={PRODUCT_IMAGE_UTILS_VER}"></script>\n  '
                + m.group(1)
            ),
            content,
        )
    content = re.sub(
        r'src="(\.\./)?assets/js/site\.js(?:\?v=[^"]+)?"',
        lambda m: f'src="{m.group(1) or ""}assets/js/site.js?v={ASSET_VER}"',
        content,
    )
    content = re.sub(
        r'href="(\.\./)?assets/css/components\.css(?:\?v=[^"]+)?"',
        lambda m: f'href="{m.group(1) or ""}assets/css/components.css?v={CSS_VER}"',
        content,
    )
    return content, content != orig


def main() -> None:
    changed: list[str] = []
    for path in ROOT.rglob("*.html"):
        if "node_modules" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        new_text, did = patch(text)
        if did:
            path.write_text(new_text, encoding="utf-8")
            changed.append(str(path.relative_to(ROOT)))
    print(f"Updated {len(changed)} files")
    for name in sorted(changed):
        print(name)


if __name__ == "__main__":
    main()
