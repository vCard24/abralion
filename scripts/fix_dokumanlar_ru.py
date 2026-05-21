# -*- coding: utf-8 -*-
from pathlib import Path

p = Path(__file__).resolve().parent.parent / "dokumanlar.html"
text = p.read_text(encoding="utf-8")
marker = "abralion_russian_cataloque.pdf"
idx = text.find(marker)
card_start = text.rfind('<div class="document-card">', 0, idx)
info_start = text.find('<div class="document-info">', card_start)
actions_end = text.find(
    '</div>\n            </div>\n          </div>\n        </div>\n\n        <div class="documents-category">',
    info_start,
)
new_block = """              <div class="document-info">
                <h3>Каталог Продукции</h3>
                <p>Полное описание всех наших продуктов на русском языке</p>
                <div class="document-meta">
                  <span class="document-size">PDF</span>
                  <span class="document-lang">Rusça</span>
                </div>
              </div>
              <div class="document-card-actions">
                <a href="assets/documents/abralion_russian_cataloque.pdf" class="btn btn-primary" download>
                  <svg class="btn-icon-svg" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                    <polyline points="7 10 12 15 17 10"/>
                    <line x1="12" y1="15" x2="12" y2="3"/>
                  </svg>
                  Скачать
                </a>
                <a href="assets/documents/abralion_russian_cataloque.pdf" class="btn btn-secondary" target="_blank" rel="noopener noreferrer">Открыть в браузере</a>
              </div>"""
text = text[:info_start] + new_block + text[actions_end:]
p.write_text(text, encoding="utf-8")
print("OK")
