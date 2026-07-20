window.I18N_MESSAGES = window.I18N_MESSAGES || {};
window.I18N_MESSAGES.ru = {
  // CompareManager / compare bar
  'compare.alreadyAdded': 'Эта модель уже добавлена в список.',
  'compare.limit': 'Можно сравнить не более {max} моделей.',
  'compare.added': 'Модель добавлена к сравнению.',
  'compare.notFound': 'Модель не найдена в списке.',
  'compare.removed': 'Модель удалена из списка.',
  'compare.selectedCount': 'Выбрано моделей: {count}',
  'compare.open': 'Сравнить',
  'compare.nav': 'Сравнение',
  'compare.addTitle': 'Добавить к сравнению',
  'compare.column': 'Сравнение',
  'compare.compareAria': 'Сравнить {label}',

  // QuoteManager / compare bar
  'quote.open': 'Запросить цену',
  'quote.alreadyAdded': 'Эта модель уже есть в списке запросов.',
  'quote.limit': 'Можно запросить цену не более чем на {max} товара.',
  'quote.added': 'Модель добавлена в список запросов.',
  'quote.notFound': 'Модель не найдена в списке.',
  'quote.removed': 'Модель удалена из списка.',

  // Header / MegaMenu
  'menu.submenuToggle': 'Открыть или закрыть подменю',
  'menu.productCategories': 'Категории продукции',
  'menu.loadError': 'Не удалось загрузить мега-меню',

  // Catalog (urunler.js)
  'catalog.count': '{count} товаров',
  'catalog.countFamilies': '{count} товарных семейств',
  'catalog.empty': 'По выбранным фильтрам товары не найдены.',
  'catalog.notFound': 'Товары не найдены.',
  'catalog.loadError': 'Не удалось загрузить товары.',
  'catalog.fallback':
    'Интерактивный каталог не загрузился. Используйте статический список ниже и страницы товаров.',
  'catalog.moduleError': 'Модуль каталога не загрузился.',
  'catalog.displayError': 'Не удалось отобразить товары.',
  'catalog.appTerms.metal': 'металл,сталь,железо,профиль,лист',
  'catalog.appTerms.inox': 'нержавейка,нержавеющая,inox',
  'catalog.appTerms.beton': 'бетон,кирпич,асфальт,стройка,строитель,отбойный,сверл,sds,бур',
  'catalog.appTerms.mermer': 'мрамор,гранит,керамика,камень',
  'catalog.appTerms.ahsap': 'дерево,столяр,макет,wood',

  // Quote form — catalog / prefill
  'quote.catalog.loadError':
    'Не удалось загрузить каталог. Убедитесь, что файл assets/js/products-data.min.js подключён.',
  'quote.catalog.notFound': 'Каталог товаров не найден (products-data.min.js)',
  'quote.catalog.emptyProducts': 'Список товаров пуст',
  'quote.catalog.emptyCategories': 'Список категорий пуст',
  'quote.compareImport.failed':
    'Не удалось перенести модели из сравнения. Выберите товары из списка.',
  'quote.prefillBanner.one':
    'Из списка сравнения добавлена 1 модель. Здесь можно изменить модель, количество и другие поля.',
  'quote.prefillBanner.many':
    'Из списка сравнения добавлено моделей: {count}. Здесь можно изменить модель, количество и другие поля.',

  // Quote form — fields
  'quote.form.selectProduct': 'Выберите товар',
  'quote.form.productLabel': 'Товар {index}',
  'quote.form.category': 'Категория *',
  'quote.form.categorySelect': 'Выберите категорию',
  'quote.form.categoryAria': 'Категория {index}',
  'quote.form.product': 'Товар *',
  'quote.form.productSelectFirst': 'Сначала выберите категорию',
  'quote.form.productSelect': 'Выберите товар',
  'quote.form.productAria': 'Товар {index}',
  'quote.form.variant': 'Модель / код *',
  'quote.form.variantSelectFirst': 'Сначала выберите товар',
  'quote.form.variantSelect': 'Выберите модель',
  'quote.form.variantAria': 'Модель {index}',
  'quote.form.qty': 'Количество',
  'quote.form.qtyOptional': 'необязательно',
  'quote.form.qtyPlaceholder': 'Шт. / коробка',
  'quote.form.qtyAria': 'Количество {index}',

  // Quote form — validation
  'quote.validation.productsRequired':
    'Выберите категорию, товар и модель хотя бы для одной позиции.',
  'quote.validation.nameRequired': 'Укажите имя и фамилию.',
  'quote.validation.phoneRequired': 'Укажите телефон.',
  'quote.validation.emailRequired': 'Укажите электронную почту.',
  'quote.validation.countryRequired': 'Укажите страну.',
  'quote.validation.cityRequired': 'Укажите город.',
  'quote.validation.emailInvalid': 'Введите действительный адрес электронной почты.',
  'quote.validation.kvkkRequired':
    'Необходимо согласие на обработку персональных данных.',
  'quote.validation.requiredFields': 'Заполните обязательные поля, отмеченные *.',
  'quote.validation.minProducts': 'Выберите хотя бы один товар.',

  // Quote form — delivery urgency
  'quote.delivery.normal': 'Обычная (1–2 недели)',
  'quote.delivery.urgent': 'Срочная (3–5 рабочих дней)',
  'quote.delivery.stock': 'Немедленно со склада',
  'quote.delivery.select': 'Выберите',

  // Quote form — PDF / print document
  'quote.document.title': 'Форма запроса цены',
  'quote.document.selectedProducts': 'Выбранные товары',
  'quote.document.contact': 'Контакты',
  'quote.document.contactInfo': 'Контактные данные',
  'quote.document.requestDetails': 'Детали запроса',
  'quote.document.noProducts': 'Товары не выбраны',
  'quote.document.noImage': 'Изображение отсутствует',
  'quote.document.productN': 'Товар {n}',
  'quote.document.qty': 'Количество',
  'quote.document.application': 'Область применения',
  'quote.document.volume': 'Объём',
  'quote.document.delivery': 'Доставка',
  'quote.document.urgency': 'Срочность',
  'quote.document.message': 'Сообщение',
  'quote.document.dateLabel': 'Дата запроса',
  'quote.document.fullName': 'Имя и фамилия',
  'quote.document.phone': 'Телефон',
  'quote.document.email': 'Электронная почта',
  'quote.document.company': 'Компания',
  'quote.document.country': 'Страна',
  'quote.document.city': 'Город',
  'quote.document.applicationArea': 'Область применения',
  'quote.document.estimatedVolume': 'Ориентировочный объём',
  'quote.document.deliveryRegion': 'Регион доставки',
  'quote.document.deliveryUrgency': 'Срочность доставки',
  'quote.document.footnote':
    'Документ является кратким изложением запроса клиента и не является обязательным коммерческим предложением.',
  'quote.document.footer':
    'EKS-PLAST LLC · info@abralion.com · www.abralion.com · 8 (495) 142-42-67',

  // Quote form — toasts
  'quote.toast.pdfDownloaded': 'PDF загружен.',
  'quote.toast.pdfModuleError': 'Модуль PDF не загрузился. Обновите страницу.',
  'quote.toast.pdfFallback':
    'Не удалось создать PDF; используйте «Сохранить как PDF» в окне печати.',
  'quote.toast.pdfHtmlFallback': 'Не удалось создать PDF; загружен HTML-файл с кратким описанием.',
  'quote.toast.printOpened': 'Открыто окно печати.',
  'quote.toast.printFallback': 'Не удалось открыть печать; загружен HTML-файл с кратким описанием.',
  'quote.toast.mailError': 'Не удалось отправить письмо.',

  'quote.print.frameTitle': 'Печать запроса',
  'quote.file.prefix': 'Abralion-Zapros',
  'quote.file.summary': 'svodka',
  'quote.mailHtmlTitle': 'Abralion — запрос цены',

  // Contact form
  'contact.validation.nameRequired': 'Введите имя и фамилию',
  'contact.validation.nameMinLength': 'Имя и фамилия должны содержать не менее 2 символов',
  'contact.validation.emailRequired': 'Введите адрес электронной почты',
  'contact.validation.emailInvalid': 'Введите действительный адрес электронной почты',
  'contact.validation.phonePattern': 'Введите действительный номер телефона',
  'contact.validation.subjectRequired': 'Укажите тему сообщения',
  'contact.validation.subjectMinLength': 'Тема должна содержать не менее 3 символов',
  'contact.validation.messageRequired': 'Введите текст сообщения',
  'contact.validation.messageMinLength': 'Сообщение должно содержать не менее 10 символов',
  'contact.validation.messageMaxLength': 'Сообщение не должно превышать 1000 символов',
  'contact.subjectQuote': 'Запрос цены — {productName}',
  'contact.success':
    '✓ Сообщение успешно отправлено! Мы свяжемся с вами в ближайшее время.',
  'contact.error': 'Не удалось отправить сообщение.',

  // FormValidator defaults
  'validation.required': 'Это поле обязательно для заполнения',
  'validation.email': 'Введите действительный адрес электронной почты',
  'validation.minLength': 'Должно быть не менее {min} символов',
  'validation.maxLength': 'Должно быть не более {max} символов',
  'validation.pattern': 'Неверный формат',
  'validation.invalid': 'Недопустимое значение',

  // Product detail
  'product.applicationImage': 'Изображение применения',
  'product.applicationImageAria': '{productName} — изображение применения',
  'product.relatedEmpty': 'Ознакомьтесь с другими товарными семействами в каталоге.',
  'product.viewDetails': 'Подробнее',
  'product.seriesPrefix': 'Серия: {series}',
  'product.breadcrumb.home': 'Главная',
  'product.breadcrumb.products': 'Продукция',
  'product.noTableConfig': 'Для этого товара не настроена таблица характеристик.',
  'product.noVariants': 'Для этого товара нет данных по вариантам.',
  'product.notFound': '{id} — товар не найден.',
  'product.loadError': 'Не удалось загрузить страницу.',
  'product.techSummaryHint':
    'Подробности по моделям см. в таблице вариантов.',
  'product.techSummary.material': 'Материал',
  'product.techSummary.diameter': 'Диаметр',
  'product.techSummary.thickness': 'Толщина',
  'product.techSummary.bore': 'Диаметр отверстия',
  'product.techSummary.maxRpm': 'Макс. об/мин',
  'product.techSummary.certificate': 'Сертификат',
  'product.techSummary.certificateValue': 'EN 12413 / oSa',

  // ProductCard
  'productCard.compareFirst': 'Добавить первую модель к сравнению',
  'productCard.compare': 'Сравнить',
  'productCard.details': 'ПОДРОБНЕЕ',
  'productCard.detailsAria': 'Подробнее о {name}',
  'productCard.industrial': 'ПРОМЫШЛЕННЫЙ',

  // Gallery / lightbox
  'gallery.dialog': 'Изображение товара',
  'gallery.close': 'Закрыть',
  'gallery.previous': 'Предыдущее изображение',
  'gallery.next': 'Следующее изображение',
  'gallery.zoom': 'Увеличить',
  'gallery.enlarge': 'Увеличить изображение',
  'gallery.thumbnails': 'Изображения товара',
  'gallery.imageN': 'Изображение {n}',

  // site.js
  'document.technicalSuffix': 'технический документ',
  'document.defaultLabel': 'Документ',
  'certification.badges': 'Знаки сертификации',
  'certification.mpa': 'MPA Hannover',
  'certification.eac': 'Знак соответствия EAC',
  'form.submit.fileOnly': 'Отправка формы доступна только на опубликованном сайте.',
  'form.submit.mailError': 'Не удалось отправить письмо. Попробуйте ещё раз.',

  // Compare page (karsilastir.js)
  'comparePage.emptyTitle': 'Список сравнения пуст',
  'comparePage.emptyHint':
    'Добавьте модели с помощью флажков в технической таблице на странице товара или выберите их в каталоге.',
  'comparePage.browseProducts': 'Перейти к продукции',
  'comparePage.loadError': 'Не удалось загрузить список.',
  'comparePage.summary': 'Сравнивается моделей: {count} из {max}',
  'comparePage.mixedNotice':
    'В таблице представлены товары из разных групп. Общие и специальные характеристики показаны вместе; неприменимые ячейки оставлены пустыми.',
  'comparePage.specsTitle': 'Технические характеристики',
  'comparePage.remove': 'Удалить',
  'comparePage.quoteInList': 'Добавлено в запрос ✓',
  'comparePage.quoteAdd': 'Добавить в запрос',
  'comparePage.viewDetails': 'Подробнее →',
  'comparePage.addModel': 'Добавить модель',
  'comparePage.browseProductsLink': 'Перейти к продукции →',
  'comparePage.requestQuote': 'Запросить цену выбранных моделей',
  'comparePage.print': 'Печать',
  'comparePage.downloadPdf': 'Скачать PDF',
  'comparePage.clearAll': 'Очистить всё',
  'comparePage.printMinOne': 'Выберите хотя бы одну модель для печати.',
  'comparePage.pdfMinOne': 'Выберите хотя бы одну модель для PDF.',
  'comparePage.pdfModuleError': 'Модуль PDF не загрузился. Обновите страницу.',
  'comparePage.pdfDownloaded': 'PDF загружен.',
  'comparePage.pdfFailed':
    'Не удалось создать PDF. Попробуйте «Сохранить как PDF» через печать.',
  'comparePage.exportTitle': 'Сравнение товаров',
  'comparePage.exportMixedNote':
    'В таблице представлены товары из разных групп; неприменимые ячейки оставлены пустыми.',
  'comparePage.exportFootnote':
    'Документ носит информационный характер и не является обязательным предложением.',

  // VariantDisplay spec column labels
  'spec.urun_kodu': 'Артикул',
  'spec.daire_capi': 'Диаметр диска Ø',
  'spec.gobek_capi': 'Диаметр посадочного отверстия Ø',
  'spec.kalinlik': 'Толщина',
  'spec.max_hiz_rpm': 'Максимальная скорость (об/мин)',
  'spec.max_hiz_ms': 'Максимальная скорость (м/с)',
  'spec.asindirici_kodu': 'Код абразива',
  'spec.asindirici_tipi': 'Тип абразива',
  'spec.grit': 'Зернистость',
  'spec.kutu': 'В упаковке',
  'spec.koli': 'В коробке',
  'spec.baglanti_tipi': 'Тип крепления',
  'spec.kafa_olcusu': 'Размер головки',
  'spec.uzunluk': 'Длина',
  'spec.urun_tipi': 'Тип изделия',
  'spec.cap_mm': 'Диаметр (мм)',
  'spec.kullanim_yeri': 'Область применения',
  'spec.kutu_ici_adet': 'Количество в упаковке',
  'spec.toplam_uzunluk': 'Общая длина (мм)',
  'spec.olcu_cap_uzunluk': 'Размер (диаметр × длина)',
  'spec.malzeme': 'Материал',
  'spec.uc_tipi': 'Тип наконечника',
  'spec.olcu_saft_uzunluk_uc': 'Размер (хвостовик × длина × ширина наконечника)',
  'spec.olcu_saft_uzunluk': 'Размер (хвостовик × длина)',
  'spec.saft_tipi': 'Тип хвостовика',
  'spec.bicak_genisligi': 'Ширина лезвия',
  'spec.govde_kizak_tipi': 'Тип корпуса / направляющей',
  'spec.bicak_malzemesi': 'Материал лезвия',
  'spec.kutu_ici': 'В упаковке',
  'spec.paket_icerigi': 'Комплектация',
  'spec.serit_genisligi': 'Ширина ленты',
  'spec.kasa_malzemesi': 'Материал корпуса',

  // Storage / legal / common
  'storage.saveError':
    'Не удалось сохранить выбор. Возможно, переполнено хранилище браузера.',
  'legal.personalData': 'Персональные данные',
  'common.clear': 'Очистить',
  'common.loadError': 'Ошибка загрузки.',
};
