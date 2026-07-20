window.I18N_MESSAGES = window.I18N_MESSAGES || {};
window.I18N_MESSAGES.tr = {
  // CompareManager / compare bar
  'compare.alreadyAdded': 'Bu model zaten listede.',
  'compare.limit': 'En fazla {max} model karşılaştırabilirsiniz.',
  'compare.added': 'Karşılaştırma listesine eklendi.',
  'compare.notFound': 'Listede bulunamadı.',
  'compare.removed': 'Listeden çıkarıldı.',
  'compare.selectedCount': '{count} model seçildi',
  'compare.open': 'Karşılaştır',
  'compare.nav': 'Karşılaştır',
  'compare.addTitle': 'Karşılaştırmaya ekle',
  'compare.column': 'Karşılaştır',
  'compare.compareAria': '{label} karşılaştır',

  // QuoteManager / compare bar
  'quote.open': 'Teklif İste',
  'quote.alreadyAdded': 'Bu model zaten teklif listesinde.',
  'quote.limit': 'En fazla {max} ürün için teklif isteyebilirsiniz.',
  'quote.added': 'Teklif listesine eklendi.',
  'quote.notFound': 'Listede bulunamadı.',
  'quote.removed': 'Listeden çıkarıldı.',

  // Header / MegaMenu
  'menu.submenuToggle': 'Alt menüyü aç/kapat',
  'menu.productCategories': 'Ürün kategorileri',
  'menu.loadError': 'Mega menü yüklenemedi',

  // Catalog (urunler.js)
  'catalog.count': '{count} ürün',
  'catalog.countFamilies': '{count} Ürün Ailesi',
  'catalog.empty': 'Seçilen filtrelere uygun ürün bulunamadı.',
  'catalog.notFound': 'Ürün bulunamadı.',
  'catalog.loadError': 'Ürünler yüklenemedi.',
  'catalog.fallback':
    'İnteraktif katalog yüklenemedi. Aşağıdaki statik liste ve ürün sayfalarını kullanabilirsiniz.',
  'catalog.moduleError': 'Ürün modülü yüklenemedi.',
  'catalog.displayError': 'Ürünler gösterilemedi.',
  'catalog.appTerms.metal': 'metal,çelik,demir,profil,sac,lama',
  'catalog.appTerms.inox': 'inox,paslanmaz',
  'catalog.appTerms.beton': 'beton,tuğla,asfalt,şantiye,inşaat,kırıcı,delici,sds,matkap',
  'catalog.appTerms.mermer': 'mermer,granit,seramik,doğal taş',
  'catalog.appTerms.ahsap': 'ahşap,marangoz,maket,tre,wood',

  // Quote form — catalog / prefill
  'quote.catalog.loadError':
    'Ürün kataloğu yüklenemedi. assets/js/products-data.min.js dosyasının yüklendiğinden emin olun.',
  'quote.catalog.notFound': 'Ürün kataloğu bulunamadı (products-data.min.js)',
  'quote.catalog.emptyProducts': 'Ürün listesi boş',
  'quote.catalog.emptyCategories': 'Kategori listesi boş',
  'quote.compareImport.failed':
    'Karşılaştırma modelleri forma aktarılamadı. Ürünleri listeden seçin.',
  'quote.prefillBanner.one':
    'Karşılaştırma listenizden 1 model aktarıldı. Model, miktar ve diğer alanları buradan düzenleyebilirsiniz.',
  'quote.prefillBanner.many':
    'Karşılaştırma listenizden {count} model aktarıldı. Model, miktar ve diğer alanları buradan düzenleyebilirsiniz.',

  // Quote form — fields
  'quote.form.selectProduct': 'Ürün seçin',
  'quote.form.productLabel': 'Ürün {index}',
  'quote.form.category': 'Kategori *',
  'quote.form.categorySelect': 'Kategori seçin',
  'quote.form.categoryAria': 'Kategori {index}',
  'quote.form.product': 'Ürün *',
  'quote.form.productSelectFirst': 'Önce kategori seçin',
  'quote.form.productSelect': 'Ürün seçin',
  'quote.form.productAria': 'Ürün {index}',
  'quote.form.variant': 'Model / Kod *',
  'quote.form.variantSelectFirst': 'Önce ürün seçin',
  'quote.form.variantSelect': 'Model seçin',
  'quote.form.variantAria': 'Model {index}',
  'quote.form.qty': 'Miktar',
  'quote.form.qtyOptional': 'opsiyonel',
  'quote.form.qtyPlaceholder': 'Adet / koli',
  'quote.form.qtyAria': 'Miktar {index}',

  // Quote form — validation
  'quote.validation.productsRequired':
    'En az bir ürün için kategori, ürün ve model seçmelisiniz.',
  'quote.validation.nameRequired': 'Ad soyad zorunludur.',
  'quote.validation.phoneRequired': 'Telefon zorunludur.',
  'quote.validation.emailRequired': 'E-posta zorunludur.',
  'quote.validation.countryRequired': 'Ülke zorunludur.',
  'quote.validation.cityRequired': 'Şehir zorunludur.',
  'quote.validation.emailInvalid': 'Geçerli bir e-posta adresi girin.',
  'quote.validation.kvkkRequired': 'KVKK onayını işaretlemeniz gerekir.',
  'quote.validation.requiredFields': 'Lütfen işaretli zorunlu alanları doldurun.',
  'quote.validation.minProducts': 'En az bir ürün seçmelisiniz.',

  // Quote form — delivery urgency
  'quote.delivery.normal': 'Normal (1–2 hafta)',
  'quote.delivery.urgent': 'Acil (3–5 iş günü)',
  'quote.delivery.stock': 'Stoktan hemen',
  'quote.delivery.select': 'Seçiniz',

  // Quote form — PDF / print document
  'quote.document.title': 'Fiyat Teklifi Talep Formu',
  'quote.document.selectedProducts': 'Seçilen ürünler',
  'quote.document.contact': 'İletişim',
  'quote.document.contactInfo': 'İletişim bilgileri',
  'quote.document.requestDetails': 'Talep detayları',
  'quote.document.noProducts': 'Ürün seçilmedi',
  'quote.document.noImage': 'Görsel yok',
  'quote.document.productN': 'Ürün {n}',
  'quote.document.qty': 'Miktar',
  'quote.document.application': 'Uygulama',
  'quote.document.volume': 'Miktar',
  'quote.document.delivery': 'Teslimat',
  'quote.document.urgency': 'Aciliyet',
  'quote.document.message': 'Mesaj',
  'quote.document.dateLabel': 'Talep tarihi',
  'quote.document.fullName': 'Ad soyad',
  'quote.document.phone': 'Telefon',
  'quote.document.email': 'E-posta',
  'quote.document.company': 'Firma',
  'quote.document.country': 'Ülke',
  'quote.document.city': 'Şehir',
  'quote.document.applicationArea': 'Uygulama alanı',
  'quote.document.estimatedVolume': 'Tahmini miktar',
  'quote.document.deliveryRegion': 'Teslimat bölgesi',
  'quote.document.deliveryUrgency': 'Teslimat aciliyeti',
  'quote.document.footnote':
    'Bu belge müşteri talep formunun özetidir; bağlayıcı fiyat teklifi niteliği taşımaz.',
  'quote.document.footer':
    'EKS-PLAST LLC · info@abralion.com · www.abralion.com · 8 (495) 142-42-67',

  // Quote form — toasts
  'quote.toast.pdfDownloaded': 'PDF indirildi.',
  'quote.toast.pdfModuleError': 'PDF modülü yüklenemedi. Sayfayı yenileyin.',
  'quote.toast.pdfFallback':
    'PDF oluşturulamadı; yazdır penceresinden “PDF olarak kaydet” kullanın.',
  'quote.toast.pdfHtmlFallback': 'PDF oluşturulamadı; özet HTML dosyası indirildi.',
  'quote.toast.printOpened': 'Yazdırma penceresi açıldı.',
  'quote.toast.printFallback': 'Yazdırma açılamadı; özet HTML dosyası indirildi.',
  'quote.toast.mailError': 'E-posta gönderilemedi.',

  'quote.print.frameTitle': 'Teklif yazdır',
  'quote.file.prefix': 'Abralion-Teklif',
  'quote.file.summary': 'ozet',
  'quote.mailHtmlTitle': 'Abralion Teklif Talebi',

  // Contact form
  'contact.validation.nameRequired': 'Lütfen adınızı ve soyadınızı girin',
  'contact.validation.nameMinLength': 'Ad soyad en az 2 karakter olmalıdır',
  'contact.validation.emailRequired': 'Lütfen e-posta adresinizi girin',
  'contact.validation.emailInvalid': 'Geçerli bir e-posta adresi girin',
  'contact.validation.phonePattern': 'Geçerli bir telefon numarası girin',
  'contact.validation.subjectRequired': 'Lütfen mesajınızın konusunu girin',
  'contact.validation.subjectMinLength': 'Konu en az 3 karakter olmalıdır',
  'contact.validation.messageRequired': 'Lütfen mesajınızı girin',
  'contact.validation.messageMinLength': 'Mesaj en az 10 karakter olmalıdır',
  'contact.validation.messageMaxLength': 'Mesaj en fazla 1000 karakter olmalıdır',
  'contact.subjectQuote': 'Fiyat Teklifi - {productName}',
  'contact.success':
    '✓ Mesajınız başarıyla gönderildi! En kısa sürede size dönüş yapacağız.',
  'contact.error': 'Gönderim başarısız.',

  // FormValidator defaults
  'validation.required': 'Bu alan zorunludur',
  'validation.email': 'Geçerli bir e-posta adresi girin',
  'validation.minLength': 'En az {min} karakter olmalıdır',
  'validation.maxLength': 'En fazla {max} karakter olmalıdır',
  'validation.pattern': 'Geçersiz format',
  'validation.invalid': 'Geçersiz değer',

  // Product detail
  'product.applicationImage': 'Uygulama görseli',
  'product.applicationImageAria': '{productName} - Uygulama görseli',
  'product.relatedEmpty': 'Katalogdan diğer ürün ailelerini inceleyebilirsiniz.',
  'product.viewDetails': 'Detayları İncele',
  'product.seriesPrefix': 'Seri: {series}',
  'product.breadcrumb.home': 'Ana Sayfa',
  'product.breadcrumb.products': 'Ürünlerimiz',
  'product.noTableConfig': 'Bu ürün için tablo yapılandırması bulunamadı.',
  'product.noVariants': 'Bu ürün için varyant verisi bulunamadı.',
  'product.notFound': '{id} — ürün bulunamadı.',
  'product.loadError': 'Sayfa yüklenemedi.',
  'product.techSummaryHint':
    'Varyasyon tablosundan model detaylarını inceleyebilirsiniz.',
  'product.techSummary.material': 'Malzeme',
  'product.techSummary.diameter': 'Çap',
  'product.techSummary.thickness': 'Kalınlık',
  'product.techSummary.bore': 'Delik Çapı',
  'product.techSummary.maxRpm': 'Max RPM',
  'product.techSummary.certificate': 'Sertifika',
  'product.techSummary.certificateValue': 'EN 12413 / oSa',

  // ProductCard
  'productCard.compareFirst': 'İlk modeli karşılaştırmaya ekle',
  'productCard.compare': 'Karşılaştır',
  'productCard.details': 'DETAYLAR',
  'productCard.detailsAria': '{name} detayları',
  'productCard.industrial': 'ENDÜSTRİYEL',

  // Gallery / lightbox
  'gallery.dialog': 'Ürün görseli',
  'gallery.close': 'Kapat',
  'gallery.previous': 'Önceki görsel',
  'gallery.next': 'Sonraki görsel',
  'gallery.zoom': 'Yakınlaştır',
  'gallery.enlarge': 'Görseli büyüt',
  'gallery.thumbnails': 'Ürün görselleri',
  'gallery.imageN': 'Görsel {n}',

  // site.js
  'document.technicalSuffix': 'teknik döküman',
  'document.defaultLabel': 'Dokuman',
  'certification.badges': 'Sertifikasyon işaretleri',
  'certification.mpa': 'MPA Hannover',
  'certification.eac': 'EAC uygunluk işareti',
  'form.submit.fileOnly': 'Form gönderimi yalnızca canlı web sitesinden yapılabilir.',
  'form.submit.mailError': 'E-posta gönderilemedi. Lütfen tekrar deneyin.',

  // Compare page (karsilastir.js)
  'comparePage.emptyTitle': 'Karşılaştırma listeniz boş',
  'comparePage.emptyHint':
    'Ürün sayfasındaki teknik tabloda satır başındaki kutucuklarla model ekleyin veya ürünler sayfasından seçim yapın.',
  'comparePage.browseProducts': 'Ürünleri İncele',
  'comparePage.loadError': 'Liste yüklenemedi.',
  'comparePage.summary': '{count} / {max} model karşılaştırılıyor',
  'comparePage.mixedNotice':
    'Farklı ürün grupları birlikte listeleniyor. Ortak ve gruba özel satırlar aynı tabloda gösterilir; ilgili olmayan hücreler boş bırakılır.',
  'comparePage.specsTitle': 'Teknik Özellikler',
  'comparePage.remove': 'Kaldır',
  'comparePage.quoteInList': 'Teklif Listesinde ✓',
  'comparePage.quoteAdd': 'Teklif Listesine Ekle',
  'comparePage.viewDetails': 'Detayları İncele →',
  'comparePage.addModel': 'Model ekle',
  'comparePage.browseProductsLink': 'Ürünleri incele →',
  'comparePage.requestQuote': 'Seçili Modeller İçin Teklif İste',
  'comparePage.print': 'Yazdır',
  'comparePage.downloadPdf': 'PDF indir',
  'comparePage.clearAll': 'Tümünü temizle',
  'comparePage.printMinOne': 'Yazdırmak için en az bir model seçin.',
  'comparePage.pdfMinOne': 'PDF için en az bir model seçin.',
  'comparePage.pdfModuleError': 'PDF modülü yüklenemedi. Sayfayı yenileyin.',
  'comparePage.pdfDownloaded': 'PDF indirildi.',
  'comparePage.pdfFailed':
    'PDF oluşturulamadı. Yazdır ile “PDF olarak kaydet” deneyin.',
  'comparePage.exportTitle': 'Ürün Karşılaştırma',
  'comparePage.exportMixedNote':
    'Farklı ürün grupları birlikte listeleniyor; ilgili olmayan hücreler boş bırakılır.',
  'comparePage.exportFootnote':
    'Bu belge bilgilendirme amaçlıdır; bağlayıcı teklif niteliği taşımaz.',

  // VariantDisplay spec column labels
  'spec.urun_kodu': 'Ürün Kodu',
  'spec.daire_capi': 'Daire Çapı Ø',
  'spec.gobek_capi': 'Göbek Çapı Ø',
  'spec.kalinlik': 'Kalınlık',
  'spec.max_hiz_rpm': 'Maksimum Hız (Rpm)',
  'spec.max_hiz_ms': 'Maksimum Hız (m/s)',
  'spec.asindirici_kodu': 'Aşındırıcı Kodu',
  'spec.asindirici_tipi': 'Aşındırıcı Tipi',
  'spec.grit': 'Grit',
  'spec.kutu': 'Kutu',
  'spec.koli': 'Koli',
  'spec.baglanti_tipi': 'Bağlantı Tipi',
  'spec.kafa_olcusu': 'Kafa Ölçüsü',
  'spec.uzunluk': 'Uzunluk',
  'spec.urun_tipi': 'Ürün Tipi',
  'spec.cap_mm': 'Çap (mm)',
  'spec.kullanim_yeri': 'Kullanım Yeri',
  'spec.kutu_ici_adet': 'Kutu İçi Adet',
  'spec.toplam_uzunluk': 'Toplam Uzunluk (mm)',
  'spec.olcu_cap_uzunluk': 'Ölçü (Çap x Uzunluk)',
  'spec.malzeme': 'Malzeme',
  'spec.uc_tipi': 'Uç Tipi',
  'spec.olcu_saft_uzunluk_uc': 'Ölçü (Şaft x Uzunluk x Uç Genişliği)',
  'spec.olcu_saft_uzunluk': 'Ölçü (Şaft x Uzunluk)',
  'spec.saft_tipi': 'Şaft Tipi',
  'spec.bicak_genisligi': 'Bıçak Genişliği',
  'spec.govde_kizak_tipi': 'Gövde / Kızak Tipi',
  'spec.bicak_malzemesi': 'Bıçak Malzemesi',
  'spec.kutu_ici': 'Kutu İçi',
  'spec.paket_icerigi': 'Paket İçeriği',
  'spec.serit_genisligi': 'Şerit Genişliği',
  'spec.kasa_malzemesi': 'Kasa Malzemesi',

  // Storage / legal / common
  'storage.saveError': 'Seçiminiz kaydedilemedi. Tarayıcı depolama alanı dolu olabilir.',
  'legal.personalData': 'KVKK',
  'common.clear': 'Temizle',
  'common.loadError': 'Yükleme başarısız.',
};
