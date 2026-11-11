# Kasım 2026 planı

Kaynak rapor: `scripts/raporlar/a0-kasim2026-rapor.md`.

Foto klasörü salt okunur kalır. A1, rapor onaylanmadan başlamaz.

## Plan değerlendirmesi

### Haklı yönler

- Önce salt okuma, sonra üretim. Onay kapısı duruyor.
- 13 foto klasörünün slug haritası katalogla uyuyor. Dört yeni slug çakışmıyor.
- Fırçalar `kesici-taslama-flap-disk`, geniş ağızlı keski `kirici-delici`. İki kimlik de `data/products.json` içinde var.
- Birebir kopyalar hash ile elenir. Dört `(1).jpg` kopyası bulundu; başka gizli kopya yok.
- `{slug}-kart.jpg` ve `{slug}-kart-card.*` korunur. Canlı kart yolu bu ada bağlı.
- Paylaşılan setler doğru: düz keski Max kareleri Plus’a, sivri murç Plus kareleri Max’e.
- Galeri formülü net: 480 + 1600, üç format.
- Bilinen düzeltmelerden ikisi gerçekten açık: ultra ince disk 2500 rpm, `Alumnum`.

### Haksız veya düzeltilen yönler

- “13 ürün klasöründe eski galeri” foto düşümünü sayıyor. Sitede eski galerisi olan slug 9. Dört yeni ürünün klasörü yok. Paylaşım iki klasör daha açar. RU ağacı ayrıca.
- Karanlık/bulanık eleme bu sete uymuyor. 188 karenin en düşük parlaklığı 216.8; hepsi beyaz stüdyo. Orientation etiketi yok. Yumuşak kuyruk işaretlendi, eleme yapılmadı.
- Dokuz ürünün metin/varyant farkı çıkarılamaz. Kasım kataloğu metni verilen girdilerde yok. Masaüstündeki docx okunmadı. Fark uydurulmadı.
- 355 mm çevresel hız düzeltmesi işi kapanmış. TR ve RU kayıtta `max_hiz_ms` 80 ve özellik metni 80 m/s. Tekrar yazılmaz.
- `Alumnum` dokuz foto ürününün içinde değil. `ao-aluminyum-oksit-flap-disk` üzerinde, dört varyant. RU metni zaten `AO Оксид алюминия`.
- Geniş keski SDS Plus yeni kaydın alanı. Yanlış eski kayıt yok. Blister karesi 14×250×40 ve SDS PLUS diyor; bu tam varyant tablosu değil.
- Yeni kartlar mevcut kart diline oturamaz. Mevcut kart 190×110, koyu kullanım karesi. Kasım seti dikey beyaz stüdyo. Dört yeni kapak stüdyo kareden kırpılır. Dokuz üründe eski kart kalır.
- Yalnız `data/products.json` yetmez. Canlı TR `assets/js/products-data.min.js` yükler. RU ayrı dosyada.
- Kök `tum-urunler/`, `tumurunler-png/`, `urun-kart-gorseller/` canlı HTML, JS ve CSS’te geçmiyor. Silme kararı bu turun içinde değil.

## Adımlar

- [x] **A0 — Keşif.** Tamamlandı. Çıktı: `scripts/raporlar/a0-kasim2026-rapor.md`. Foto klasörüne yazılmadı, commit yok.
- [x] **A0 onayı.** A1a pilotu bu onayla açıldı.
- [x] **A1a pilot.** Yalnız `miknatisli-anahtar-ucu` galerisi ve `canak-firca-sacakli` kart örnekleri (siteye bağlı değil). Rapor: `scripts/raporlar/a1a-pilot-rapor.md`.
- [ ] **A1b.** Kalan 12 foto klasörü, 4 yeni ürün klasörü, kardeş bağlama (düz keski Plus, sivri murç Max). Onay bekler. Mevcut `{slug}-kart.jpg` dosyalarına dokunulmaz.
- [ ] **A1c — Eski galeri.** Dokuz slug + iki paylaşım hedefi, TR ve RU. Korunanlar yalnızca `{slug}-kart.jpg` ve `{slug}-kart-card.*`.
- [ ] **A1d — Katalog.** Dört yeni iskelet. `max_hiz_rpm` 2500 → 12200. `Alumnum` → `Aluminum` (yalnız TR). 355 mm hızına dokunulmaz. Ardından `products-data.js` senkronu ve RU kopyası.
- [ ] **A1e — Metin farkı.** Kasım kataloğu dosyası girdi olarak verilirse dokuz ürünün ad, açıklama ve varyant tablosu karşılaştırılır. O dosya gelmeden varyant satırı yazılmaz.

## A1’de kapanmış sayılanlar

- Klasör → slug haritası.
- Kategori kimlikleri.
- Dört kopyanın elenecek listesi.
- 355 mm için 80 m/s (veri zaten doğru).
- Kart koruma kuralının kapsamı.
