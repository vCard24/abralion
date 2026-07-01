#!/usr/bin/env python3
"""Point HTML script tags to products-data.min.js."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TARGET = "products-data.min.js?v=20260703"
PATTERN = re.compile(
    r'(<script(?: defer)? src="(?:\.\./)?assets/js/)products-data\.js(?:\?v=[^"]+)?("></script>)'
)


def patch_file(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")
    new_text = PATTERN.sub(rf"\1{TARGET}\2", text)
    if new_text != text:
        path.write_text(new_text, encoding="utf-8")
        return True
    return False


def main() -> None:
    changed: list[str] = []
    for path in sorted(ROOT.rglob("*.html")):
        if "node_modules" in path.parts:
            continue
        if patch_file(path):
            changed.append(str(path.relative_to(ROOT)))
    print(f"Updated {len(changed)} files")
    for name in changed:
        print(name)


if __name__ == "__main__":
    main()
