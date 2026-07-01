<?php
/**
 * ═══════════════════════════════════════════════════════════════════════════
 * ABRALION — Hostinger e-posta yapılandırması
 * ═══════════════════════════════════════════════════════════════════════════
 *
 * KURULUM (hPanel → Dosya Yöneticisi):
 * 1. public_html/api/ klasörünün olduğundan emin olun (git push sonrası yükleyin)
 * 2. Bu dosyayı kopyalayıp adını config.php yapın
 * 3. smtp_pass satırına info@abralion.com hesabının şifresini yazın
 * 4. https://abralion.com/iletisim.html formunu test edin
 *
 * Hostinger SMTP (hPanel → E-postalar → info@abralion.com → Bağlantı ayarları):
 *   Sunucu : smtp.hostinger.com
 *   Port   : 465 (SSL)  — alternatif: 587 (TLS, smtp_secure => 'tls')
 *   Kullanıcı: info@abralion.com
 *
 * NOT: noreply@ hesabı gerekmez. Gönderen ve alıcı info@ olabilir.
 *      Yanıt (Reply-To) formu dolduran ziyaretçinin e-postasına gider.
 *
 * config.php repoya eklenmez (.gitignore).
 */
return [
    'mail_to' => 'info@abralion.com',
    'mail_from' => 'info@abralion.com',
    'mail_from_name' => 'Abralion Web Formu',

    'use_smtp' => true,
    'smtp_host' => 'smtp.hostinger.com',
    'smtp_port' => 465,
    'smtp_secure' => 'ssl',
    'smtp_user' => 'info@abralion.com',
    'smtp_pass' => 'BURAYA_INFO_EPOSTA_SIFRESI',

    'allowed_origins' => [
        'https://abralion.com',
        'https://www.abralion.com',
    ],

    /** Görsellerin mutlak URL'si için (e-posta şablonu) */
    'site_url' => 'https://abralion.com',

    /** true ise SMTP yerine api/outbox/ klasörüne kaydeder (test) */
    'dev_save_only' => false,
];
