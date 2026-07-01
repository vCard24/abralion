#!/usr/bin/env python3
"""Repair perf head patches: nested noscript and theme script placement."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

THEME_SNIPPET = (
    '<script>document.documentElement.classList.add("dark-theme","dark");'
    'document.body.classList.add("dark-theme");</script>'
)

NESTED_NOSCRIPT = re.compile(
    r"<noscript>\s*<link rel=\"preload\"[^>]+onload[^>]+>\s*"
    r"<noscript>(<link rel=\"stylesheet\"[^>]+>)</noscript>\s*</noscript>",
    re.MULTILINE,
)

HEAD_THEME = re.compile(
    r"</head>\s*<script>document\.documentElement\.classList\.add\(\"dark-theme\",\"dark\"\);</script>\s*",
    re.MULTILINE,
)

BODY_THEME_DUP = re.compile(
    r"(<body[^>]*>)\s*"
    r"(?:<script>document\.documentElement\.classList\.add\([\"']dark-theme[\"'],[\"']dark[\"']\);"
    r"document\.body\.classList\.add\([\"']dark-theme[\"']\);</script>\s*)+",
    re.MULTILINE,
)


def patch(content: str) -> str:
    content = NESTED_NOSCRIPT.sub(r"<noscript>\1</noscript>", content)
    content = HEAD_THEME.sub("</head>\n", content)
    content = BODY_THEME_DUP.sub(r"\1\n  " + THEME_SNIPPET + "\n", content)

    if THEME_SNIPPET not in content:
        content = re.sub(
            r"(<body[^>]*>)",
            r"\1\n  " + THEME_SNIPPET,
            content,
            count=1,
        )

    return content


def main() -> None:
    changed = []
    for path in sorted(ROOT.rglob("*.html")):
        if "node_modules" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        new_text = patch(text)
        if new_text != text:
            path.write_text(new_text, encoding="utf-8")
            changed.append(str(path.relative_to(ROOT)))
    print(f"Repaired {len(changed)} files")
    for name in changed:
        print(name)


if __name__ == "__main__":
    main()
