<?php
declare(strict_types=1);

/**
 * Fiyat teklifi formu — yapılandırılmış JSON'dan HTML e-posta üretir.
 */

function abr_quote_h(string $s): string
{
    return htmlspecialchars($s, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');
}

function abr_quote_site_url(array $config = []): string
{
    $url = rtrim(trim((string) ($config['site_url'] ?? 'https://abralion.com')), '/');
    return $url !== '' ? $url : 'https://abralion.com';
}

function abr_quote_email_section(string $title, string $bodyHtml): string
{
    return '<table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="margin:0 0 14px;border:1px solid #e5e7eb;border-radius:8px;border-collapse:separate;overflow:hidden;background:#ffffff;">'
        . '<tr><td style="padding:8px 14px;background:#f3f4f6;border-bottom:1px solid #e5e7eb;font-family:Arial,Helvetica,sans-serif;font-size:10px;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;color:#374151;">'
        . abr_quote_h($title)
        . '</td></tr><tr><td style="padding:14px;font-family:Arial,Helvetica,sans-serif;font-size:13px;line-height:1.5;color:#111827;">'
        . $bodyHtml
        . '</td></tr></table>';
}

/** @param array<int,array{0:string,1:string}> $fields */
function abr_quote_field_table(array $fields): string
{
    $rows = '';
    foreach ($fields as $row) {
        $label = trim((string) ($row[0] ?? ''));
        $value = trim((string) ($row[1] ?? ''));
        if ($value === '') {
            continue;
        }
        $rows .= '<tr><td style="padding:6px 10px 6px 0;width:38%;vertical-align:top;font-size:11px;font-weight:700;color:#6b7280;text-transform:uppercase;letter-spacing:0.04em;">'
            . abr_quote_h($label)
            . '</td><td style="padding:6px 0;vertical-align:top;font-size:13px;color:#111827;">'
            . abr_quote_h($value)
            . '</td></tr>';
    }
    if ($rows === '') {
        return '<p style="margin:0;color:#6b7280;">—</p>';
    }
    return '<table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="border-collapse:collapse;">' . $rows . '</table>';
}

function abr_quote_urgency_label(string $value): string
{
    return match ($value) {
        'normal' => 'Normal (1–2 hafta)',
        'urgent' => 'Acil (3–5 iş günü)',
        'stock' => 'Stoktan hemen',
        default => $value,
    };
}

/** @param array<string,mixed> $row */
function abr_quote_product_image_cell(array $row): string
{
    $imgUrl = trim((string) ($row['imageUrl'] ?? ''));
    if ($imgUrl !== '' && preg_match('#^https?://#i', $imgUrl) && !str_starts_with(strtolower($imgUrl), 'data:')) {
        $alt = abr_quote_h((string) ($row['productName'] ?? 'Ürün'));
        return '<img src="' . abr_quote_h($imgUrl) . '" alt="' . $alt . '" width="120" style="display:block;width:120px;max-width:120px;height:auto;border-radius:6px;border:1px solid #e5e7eb;background:#fff;" />';
    }
    return '<div style="width:120px;height:90px;border:1px dashed #d1d5db;border-radius:6px;background:#f9fafb;color:#9ca3af;font-size:11px;line-height:90px;text-align:center;">Görsel yok</div>';
}

/** @param array<string,mixed> $row */
function abr_quote_product_specs_html(array $row): string
{
    $specLines = $row['specLines'] ?? [];
    $rows = '';
    if (is_array($specLines)) {
        foreach ($specLines as $spec) {
            if (!is_array($spec)) {
                continue;
            }
            $label = trim((string) ($spec['label'] ?? ''));
            $value = trim((string) ($spec['value'] ?? ''));
            if ($label === '' || $value === '') {
                continue;
            }
            $rows .= '<tr><td style="padding:2px 12px 2px 0;color:#6b7280;">'
                . abr_quote_h($label)
                . '</td><td style="padding:2px 0;font-weight:600;">'
                . abr_quote_h($value)
                . '</td></tr>';
        }
    }

    $qty = trim((string) ($row['qty'] ?? ''));
    if ($qty !== '') {
        $rows .= '<tr><td style="padding:2px 12px 2px 0;color:#6b7280;">Miktar</td><td style="padding:2px 0;font-weight:600;">'
            . abr_quote_h($qty)
            . '</td></tr>';
    }

    if ($rows === '') {
        return '';
    }
    return '<table role="presentation" cellspacing="0" cellpadding="0" style="margin:8px 0 0;font-size:12px;color:#374151;">' . $rows . '</table>';
}

/** @param array<string,mixed> $data */
function abr_quote_product_cards(array $data): string
{
    $products = $data['products'] ?? [];
    if (!is_array($products) || !$products) {
        return '<p style="margin:0;color:#6b7280;">Ürün seçilmedi</p>';
    }

    $cards = [];
    $n = 0;
    foreach ($products as $row) {
        if (!is_array($row)) {
            continue;
        }
        $name = trim((string) ($row['productName'] ?? ''));
        $model = trim((string) ($row['label'] ?? ''));
        if ($name === '' && $model === '') {
            continue;
        }
        $n++;

        $category = trim((string) ($row['categoryName'] ?? ''));
        $description = trim((string) ($row['description'] ?? ''));
        if (strlen($description) > 220) {
            $description = substr($description, 0, 217) . '…';
        }

        $productUrl = trim((string) ($row['productUrl'] ?? ''));
        $titleHtml = abr_quote_h($name !== '' ? $name : 'Ürün');
        if ($productUrl !== '' && preg_match('#^https?://#i', $productUrl)) {
            $titleHtml = '<a href="' . abr_quote_h($productUrl) . '" style="color:#111827;text-decoration:none;font-weight:700;">'
                . abr_quote_h($name !== '' ? $name : 'Ürün')
                . '</a>';
        }

        $meta = [];
        if ($category !== '') {
            $meta[] = abr_quote_h($category);
        }
        if ($model !== '') {
            $meta[] = 'Model: ' . abr_quote_h($model);
        }

        $descHtml = $description !== ''
            ? '<p style="margin:8px 0 0;font-size:12px;line-height:1.45;color:#4b5563;">' . abr_quote_h($description) . '</p>'
            : '';

        $cards[] = '<table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="margin:0 0 10px;border:1px solid #e5e7eb;border-radius:8px;border-collapse:separate;overflow:hidden;">'
            . '<tr><td colspan="2" style="padding:6px 12px;background:#fef2f2;font-family:Arial,Helvetica,sans-serif;font-size:11px;font-weight:700;color:#E2231A;">Ürün '
            . $n
            . '</td></tr><tr><td style="padding:12px;width:132px;vertical-align:top;background:#fff;">'
            . abr_quote_product_image_cell($row)
            . '</td><td style="padding:12px;vertical-align:top;background:#fff;font-family:Arial,Helvetica,sans-serif;">'
            . '<p style="margin:0 0 4px;font-size:16px;font-weight:700;color:#111827;">' . $titleHtml . '</p>'
            . ($meta !== [] ? '<p style="margin:0 0 6px;font-size:12px;color:#6b7280;">' . implode(' · ', $meta) . '</p>' : '')
            . abr_quote_product_specs_html($row)
            . $descHtml
            . '</td></tr></table>';
    }

    return $cards !== [] ? implode('', $cards) : '<p style="margin:0;color:#6b7280;">Ürün seçilmedi</p>';
}

/** @param array<string,mixed> $data */
function abr_normalize_quote_form_data(array $data): array
{
    return [
        'reference' => trim((string) ($data['reference'] ?? '—')),
        'name' => trim((string) ($data['name'] ?? '')),
        'phone' => trim((string) ($data['phone'] ?? '')),
        'email' => trim((string) ($data['email'] ?? '')),
        'company' => trim((string) ($data['company'] ?? '')),
        'country' => trim((string) ($data['country'] ?? '')),
        'city' => trim((string) ($data['city'] ?? '')),
        'application' => trim((string) ($data['application'] ?? '')),
        'volume' => trim((string) ($data['volume'] ?? '')),
        'delivery' => trim((string) ($data['delivery'] ?? '')),
        'urgency' => trim((string) ($data['urgency'] ?? '')),
        'message' => trim((string) ($data['message'] ?? '')),
        'products' => is_array($data['products'] ?? null) ? $data['products'] : [],
    ];
}

/** @param array<string,mixed> $data */
function abr_build_quote_email_html(array $data, array $config = []): string
{
    $data = abr_normalize_quote_form_data($data);
    $siteUrl = abr_quote_site_url($config);
    $dateStr = date('d.m.Y H:i');
    $logoSrc = $siteUrl . '/assets/images/logo.svg';
    $logoHtml = '<img src="' . abr_quote_h($logoSrc) . '" alt="Abralion" width="160" style="display:block;width:160px;max-width:160px;height:auto;" />';

    $refLine = $data['reference'] !== '' && $data['reference'] !== '—'
        ? '<p style="margin:4px 0 0;font-size:11px;color:#E2231A;font-weight:700;">Referans: ' . abr_quote_h($data['reference']) . '</p>'
        : '';

    $contactHtml = abr_quote_field_table([
        ['Ad soyad', $data['name']],
        ['Telefon', $data['phone']],
        ['E-posta', $data['email']],
        ['Firma', $data['company']],
        ['Ülke', $data['country']],
        ['Şehir', $data['city']],
    ]);

    $detailsHtml = abr_quote_field_table([
        ['Uygulama alanı', $data['application']],
        ['Tahmini miktar', $data['volume']],
        ['Teslimat bölgesi', $data['delivery']],
        ['Teslimat aciliyeti', abr_quote_urgency_label($data['urgency'])],
        ['Mesaj / not', $data['message']],
    ]);

    $detailsBlock = str_contains($detailsHtml, '<tr>')
        ? abr_quote_email_section('Talep detayları', $detailsHtml)
        : '';

    return '<!DOCTYPE html><html lang="tr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Fiyat Teklifi Talebi — Abralion</title></head>'
        . '<body style="margin:0;padding:0;background:#f3f4f6;">'
        . '<table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background:#f3f4f6;padding:24px 12px;">'
        . '<tr><td align="center">'
        . '<table role="presentation" width="640" cellspacing="0" cellpadding="0" style="max-width:640px;width:100%;background:#ffffff;border:1px solid #e5e7eb;border-radius:10px;overflow:hidden;">'
        . '<tr><td style="padding:24px 28px 16px;border-bottom:2px solid #E2231A;font-family:Arial,Helvetica,sans-serif;">'
        . '<table role="presentation" width="100%" cellspacing="0" cellpadding="0"><tr>'
        . '<td style="width:170px;vertical-align:middle;">' . $logoHtml . '</td>'
        . '<td style="vertical-align:middle;padding-left:16px;">'
        . '<h1 style="margin:0 0 4px;font-size:21px;line-height:1.25;color:#111827;">Fiyat Teklifi Talebi</h1>'
        . '<p style="margin:0;font-size:11px;color:#6b7280;">Talep tarihi: ' . abr_quote_h($dateStr) . '</p>'
        . $refLine
        . '</td></tr></table></td></tr>'
        . '<tr><td style="padding:20px 28px 8px;">'
        . abr_quote_email_section('Seçilen ürünler', abr_quote_product_cards($data))
        . abr_quote_email_section('İletişim bilgileri', $contactHtml)
        . $detailsBlock
        . '</td></tr>'
        . '<tr><td style="padding:0 28px 24px;font-family:Arial,Helvetica,sans-serif;font-size:11px;line-height:1.6;color:#6b7280;border-top:1px solid #e5e7eb;">'
        . '<p style="margin:16px 0 6px;"><strong style="color:#111827;">Abralion — EKS-PLAST LLC</strong><br />'
        . abr_quote_h($siteUrl) . ' · info@abralion.com · +7 985 789-60-62</p>'
        . '<p style="margin:0;font-size:10px;">Bu belge müşteri talep formunun özetidir; bağlayıcı fiyat teklifi niteliği taşımaz.</p>'
        . '</td></tr></table></td></tr></table></body></html>';
}

/** @param array<string,mixed> $data */
function abr_build_quote_email_plain(array $data): string
{
    $data = abr_normalize_quote_form_data($data);
    $lines = [
        'ABRALION — FİYAT TEKLİFİ TALEBİ',
        'Referans: ' . $data['reference'],
        'Tarih: ' . date('d.m.Y H:i'),
        '',
        '--- İLETİŞİM ---',
        'Ad: ' . $data['name'],
        'Tel: ' . $data['phone'],
        'E-posta: ' . $data['email'],
        'Firma: ' . ($data['company'] !== '' ? $data['company'] : '—'),
        'Ülke: ' . $data['country'],
        'Şehir: ' . $data['city'],
        '',
        '--- TALEP ---',
        'Uygulama: ' . ($data['application'] !== '' ? $data['application'] : '—'),
        'Miktar: ' . ($data['volume'] !== '' ? $data['volume'] : '—'),
        'Teslimat: ' . ($data['delivery'] !== '' ? $data['delivery'] : '—'),
        'Aciliyet: ' . ($data['urgency'] !== '' ? abr_quote_urgency_label($data['urgency']) : '—'),
        'Mesaj: ' . ($data['message'] !== '' ? $data['message'] : '—'),
        '',
        '--- ÜRÜNLER ---',
    ];

    foreach ($data['products'] as $i => $row) {
        if (!is_array($row)) {
            continue;
        }
        $name = trim((string) ($row['productName'] ?? ''));
        $model = trim((string) ($row['label'] ?? ''));
        $qty = trim((string) ($row['qty'] ?? ''));
        $lines[] = ($i + 1) . '. ' . ($name !== '' ? $name : 'Ürün');
        if ($model !== '') {
            $lines[] = '   Model: ' . $model . ($qty !== '' ? ' | Miktar: ' . $qty : '');
        }
    }

    return implode("\n", $lines);
}

function abr_strip_data_urls_from_html(string $html): string
{
    return (string) preg_replace('/src=(["\'])data:[^"\']+\1/i', 'src=$1$1', $html);
}

/** @param array<string,mixed> $data */
function abr_normalize_contact_form_data(array $data): array
{
    return [
        'name' => trim((string) ($data['name'] ?? '')),
        'email' => trim((string) ($data['email'] ?? '')),
        'phone' => trim((string) ($data['phone'] ?? '')),
        'subject' => trim((string) ($data['subject'] ?? '')),
        'message' => trim((string) ($data['message'] ?? '')),
    ];
}

/** @param array<string,mixed> $data */
function abr_build_contact_email_html(array $data, array $config = []): string
{
    $data = abr_normalize_contact_form_data($data);
    $siteUrl = abr_quote_site_url($config);
    $dateStr = date('d.m.Y H:i');
    $logoSrc = $siteUrl . '/assets/images/logo.svg';
    $logoHtml = '<img src="' . abr_quote_h($logoSrc) . '" alt="Abralion" width="160" style="display:block;width:160px;max-width:160px;height:auto;" />';

    $subjectLine = $data['subject'] !== ''
        ? '<p style="margin:4px 0 0;font-size:11px;color:#E2231A;font-weight:700;">Konu: ' . abr_quote_h($data['subject']) . '</p>'
        : '';

    $senderHtml = abr_quote_field_table([
        ['Ad soyad', $data['name']],
        ['E-posta', $data['email']],
        ['Telefon', $data['phone'] !== '' ? $data['phone'] : '—'],
        ['Konu', $data['subject']],
    ]);

    $messageHtml = $data['message'] !== ''
        ? '<div style="margin:0;padding:14px;background:#f9fafb;border:1px solid #e5e7eb;border-radius:8px;font-family:Arial,Helvetica,sans-serif;font-size:14px;line-height:1.6;color:#111827;white-space:pre-wrap;">'
            . nl2br(abr_quote_h($data['message']))
            . '</div>'
        : '<p style="margin:0;color:#6b7280;">—</p>';

    $ip = trim((string) ($_SERVER['REMOTE_ADDR'] ?? '—'));
    $metaLine = '<p style="margin:12px 0 0;font-size:10px;color:#9ca3af;">Gönderim: '
        . abr_quote_h($dateStr)
        . ' · IP: '
        . abr_quote_h($ip !== '' ? $ip : '—')
        . '</p>';

    return '<!DOCTYPE html><html lang="tr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>İletişim Formu — Abralion</title></head>'
        . '<body style="margin:0;padding:0;background:#f3f4f6;">'
        . '<table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="background:#f3f4f6;padding:24px 12px;">'
        . '<tr><td align="center">'
        . '<table role="presentation" width="640" cellspacing="0" cellpadding="0" style="max-width:640px;width:100%;background:#ffffff;border:1px solid #e5e7eb;border-radius:10px;overflow:hidden;">'
        . '<tr><td style="padding:24px 28px 16px;border-bottom:2px solid #E2231A;font-family:Arial,Helvetica,sans-serif;">'
        . '<table role="presentation" width="100%" cellspacing="0" cellpadding="0"><tr>'
        . '<td style="width:170px;vertical-align:middle;">' . $logoHtml . '</td>'
        . '<td style="vertical-align:middle;padding-left:16px;">'
        . '<h1 style="margin:0 0 4px;font-size:21px;line-height:1.25;color:#111827;">İletişim Formu</h1>'
        . '<p style="margin:0;font-size:11px;color:#6b7280;">Talep tarihi: ' . abr_quote_h($dateStr) . '</p>'
        . $subjectLine
        . '</td></tr></table></td></tr>'
        . '<tr><td style="padding:20px 28px 8px;">'
        . abr_quote_email_section('Gönderen bilgileri', $senderHtml)
        . abr_quote_email_section('Mesaj', $messageHtml . $metaLine)
        . '</td></tr>'
        . '<tr><td style="padding:0 28px 24px;font-family:Arial,Helvetica,sans-serif;font-size:11px;line-height:1.6;color:#6b7280;border-top:1px solid #e5e7eb;">'
        . '<p style="margin:16px 0 6px;"><strong style="color:#111827;">Abralion — EKS-PLAST LLC</strong><br />'
        . abr_quote_h($siteUrl) . ' · info@abralion.com · +7 985 789-60-62</p>'
        . '<p style="margin:0;font-size:10px;">Bu e-posta web sitesi iletişim formundan otomatik gönderilmiştir.</p>'
        . '</td></tr></table></td></tr></table></body></html>';
}

/** @param array<string,mixed> $data */
function abr_build_contact_email_plain(array $data): string
{
    $data = abr_normalize_contact_form_data($data);
    $ip = trim((string) ($_SERVER['REMOTE_ADDR'] ?? '—'));

    return implode("\n", [
        'ABRALION — İLETİŞİM FORMU',
        'Tarih: ' . date('d.m.Y H:i'),
        '',
        '--- GÖNDEREN ---',
        'Ad Soyad: ' . $data['name'],
        'E-posta: ' . $data['email'],
        'Telefon: ' . ($data['phone'] !== '' ? $data['phone'] : '—'),
        'Konu: ' . $data['subject'],
        '',
        '--- MESAJ ---',
        $data['message'],
        '',
        'Gönderim: ' . date('d.m.Y H:i:s'),
        'IP: ' . ($ip !== '' ? $ip : '—'),
    ]);
}
