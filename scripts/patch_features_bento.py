from pathlib import Path

D = chr(100) + chr(105) + chr(118)  # div


def el(classes: str, inner: str) -> str:
    return f"        <{D} class=\"{classes}\">\n{inner}\n        </{D}>\n"


def card(icon: str, title: str, text: str) -> str:
    inner = f"""          <span class="material-symbols-outlined text-abrasive-red text-4xl mb-4" data-icon="{icon}">{icon}</span>
          <h3 class="font-headline-md text-headline-md text-white mb-2">{title}</h3>
          <p class="font-body-md text-body-md text-secondary">{text}</p>
          <span class="material-symbols-outlined absolute top-4 right-4 text-white/10 group-hover:text-abrasive-red transition-colors" data-icon="north_east">north_east</span>"""
    return el(
        "bg-surface-elevation technical-border p-8 hover:bg-surface-container-high transition-all group relative overflow-hidden",
        inner,
    )


cards = [
    ("verified", "Uluslararası Kalite", "Standartlara uygun, sertifikalı üretim süreçleri."),
    ("local_shipping", "Rusya'da Teslimat", "Kendi lojistik ağımızla kapıdan kapıya teslim."),
    ("support_agent", "Teknik Destek", "Uzman mühendis kadromuzla anında çözüm."),
    ("timer", "Hızlı Teklif", "İhtiyaçlarınıza 24 saat içinde yanıt garantisi."),
]

bento = "    <!-- Features Bento -->\n"
bento += '    <section class="py-section-gap max-w-7xl mx-auto px-margin-desktop">\n'
bento += f'      <{D} class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-gutter">\n'
for icon, title, text in cards:
    bento += card(icon, title, text)
bento += f"      </{D}>\n"
bento += "    </section>\n\n"

path = Path(__file__).resolve().parents[1] / "index.html"
text = path.read_text(encoding="utf-8")

start = text.index("        <!-- Güven kartları")
end = text.index("    <!-- Category Showcase -->")

hero_close = "      </div>\n    </section>\n\n"
new_text = text[:start] + hero_close + bento + text[end:]
path.write_text(new_text, encoding="utf-8")
print("Patched index.html: removed home-trust strip, added Features Bento.")
