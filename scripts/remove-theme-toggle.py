# -*- coding: utf-8 -*-
"""Tüm HTML dosyalarından ThemeToggle.js script satırını kaldırır."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LINES = (
    '  <script defer src="assets/js/ThemeToggle.js"></script>\n',
    '  <script defer src="../assets/js/ThemeToggle.js"></script>\n',
)

def main():
    count = 0
    for path in ROOT.rglob('*.html'):
        text = path.read_text(encoding='utf-8')
        new = text
        for line in LINES:
            new = new.replace(line, '')
        if new != text:
            path.write_text(new, encoding='utf-8')
            count += 1
    print(f'OK: {count} HTML dosyası güncellendi')


if __name__ == '__main__':
    main()
