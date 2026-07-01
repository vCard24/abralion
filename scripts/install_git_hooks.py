#!/usr/bin/env python3
"""Copy scripts/hooks/* into .git/hooks/ (no git config changes)."""
from __future__ import annotations

import shutil
import stat
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = ROOT / "scripts" / "hooks"
DEST_DIR = ROOT / ".git" / "hooks"


def main() -> int:
    if not DEST_DIR.parent.is_dir():
        print(".git klasörü yok; bu depo bir git reposu değil.", file=sys.stderr)
        return 1

    installed = 0
    for hook in sorted(SRC_DIR.iterdir()):
        if not hook.is_file() or hook.name.endswith(".py"):
            continue
        target = DEST_DIR / hook.name
        shutil.copy2(hook, target)
        target.chmod(target.stat().st_mode | stat.S_IEXEC)
        print(f"Kuruldu: {target.relative_to(ROOT)}")
        installed += 1

    if not installed:
        print(f"Hook bulunamadı: {SRC_DIR}", file=sys.stderr)
        return 1

    print(f"{installed} git hook kuruldu.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
