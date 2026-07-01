<?php
/**
 * Hostinger api/config.php şablonu (repoya config.php eklenmez).
 * Sunucuda: bu içeriği api/config.php olarak kaydedin, smtp_pass doldurun.
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

    'site_url' => 'https://abralion.com',
    'dev_save_only' => false,
];
