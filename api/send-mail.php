<?php
declare(strict_types=1);

header('Content-Type: application/json; charset=utf-8');

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['ok' => false, 'error' => 'Yalnızca POST desteklenir.']);
    exit;
}

$configPath = __DIR__ . '/config.php';
if (!is_file($configPath)) {
    http_response_code(503);
    echo json_encode([
        'ok' => false,
        'error' => 'Sunucu e-posta yapılandırması eksik. api/config.php oluşturulmalı.',
    ]);
    exit;
}

/** @var array<string, mixed> $config */
$config = require $configPath;

validateConfig($config);

$raw = file_get_contents('php://input') ?: '';
$data = json_decode($raw, true);
if (!is_array($data)) {
    http_response_code(400);
    echo json_encode(['ok' => false, 'error' => 'Geçersiz istek gövdesi.']);
    exit;
}

if (!empty($data['website'])) {
    echo json_encode(['ok' => true]);
    exit;
}

$type = (string) ($data['type'] ?? '');
if (!in_array($type, ['contact', 'quote'], true)) {
    http_response_code(400);
    echo json_encode(['ok' => false, 'error' => 'Geçersiz form türü.']);
    exit;
}

try {
    if ($type === 'contact') {
        [$subject, $body, $replyTo] = buildContactMail($data);
    } else {
        [$subject, $body, $replyTo] = buildQuoteMail($data);
    }

    sendMail($config, (string) $config['mail_to'], $subject, $body, normalizeReplyTo($replyTo, $config));
    echo json_encode(['ok' => true]);
} catch (Throwable $e) {
    error_log('Abralion send-mail: ' . $e->getMessage());
    http_response_code(500);
    echo json_encode(['ok' => false, 'error' => 'E-posta gönderilemedi. Lütfen daha sonra tekrar deneyin.']);
}

function validateConfig(array $config): void
{
    $pass = (string) ($config['smtp_pass'] ?? '');
    if (!empty($config['use_smtp']) && ($pass === '' || str_contains($pass, 'BURAYA_'))) {
        http_response_code(503);
        echo json_encode([
            'ok' => false,
            'error' => 'SMTP şifresi yapılandırılmamış. api/config.php dosyasını düzenleyin.',
        ]);
        exit;
    }

    enforceOrigin($config['allowed_origins'] ?? []);
}

function enforceOrigin(array $allowed): void
{
    $origin = $_SERVER['HTTP_ORIGIN'] ?? '';
    if ($origin === '' || !$allowed) {
        return;
    }
    if (!in_array($origin, $allowed, true)) {
        http_response_code(403);
        echo json_encode(['ok' => false, 'error' => 'İzin verilmeyen kaynak.']);
        exit;
    }
}

function buildContactMail(array $data): array
{
    $name = trim((string) ($data['name'] ?? ''));
    $email = trim((string) ($data['email'] ?? ''));
    $phone = trim((string) ($data['phone'] ?? ''));
    $subjectLine = trim((string) ($data['subject'] ?? ''));
    $message = trim((string) ($data['message'] ?? ''));

    if ($name === '' || $email === '' || $subjectLine === '' || $message === '') {
        throw new InvalidArgumentException('Zorunlu alanlar eksik.');
    }
    if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
        throw new InvalidArgumentException('Geçersiz e-posta.');
    }

    $subject = '[Abralion İletişim] ' . $subjectLine;
    $body = implode("\n", [
        'Yeni iletişim formu mesajı',
        '========================',
        'Ad Soyad: ' . $name,
        'E-posta: ' . $email,
        'Telefon: ' . ($phone !== '' ? $phone : '—'),
        'Konu: ' . $subjectLine,
        '',
        'Mesaj:',
        $message,
        '',
        'Gönderim: ' . date('d.m.Y H:i:s'),
        'IP: ' . ($_SERVER['REMOTE_ADDR'] ?? '—'),
    ]);

    return [$subject, $body, $email];
}

function buildQuoteMail(array $data): array
{
    $name = trim((string) ($data['name'] ?? ''));
    $email = trim((string) ($data['email'] ?? ''));
    $phone = trim((string) ($data['phone'] ?? ''));
    if ($name === '' || $email === '' || $phone === '') {
        throw new InvalidArgumentException('Zorunlu alanlar eksik.');
    }
    if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
        throw new InvalidArgumentException('Geçersiz e-posta.');
    }

    $reference = trim((string) ($data['reference'] ?? '—'));
    $subject = '[Abralion Teklif] ' . $name . ' — ' . $reference;

    $lines = [
        'Yeni fiyat teklifi talebi',
        '=========================',
        'Referans: ' . $reference,
        'Ad Soyad: ' . $name,
        'Telefon: ' . $phone,
        'E-posta: ' . $email,
        'Firma: ' . trim((string) ($data['company'] ?? '')) ?: '—',
        'Ülke: ' . trim((string) ($data['country'] ?? '')),
        'Şehir: ' . trim((string) ($data['city'] ?? '')),
        'Uygulama: ' . trim((string) ($data['application'] ?? '')) ?: '—',
        'Miktar: ' . trim((string) ($data['volume'] ?? '')) ?: '—',
        'Teslimat: ' . trim((string) ($data['delivery'] ?? '')) ?: '—',
        'Aciliyet: ' . trim((string) ($data['urgency'] ?? '')) ?: '—',
        '',
        'Mesaj:',
        trim((string) ($data['message'] ?? '')) ?: '—',
        '',
        '--- ÜRÜNLER ---',
    ];

    $products = $data['products'] ?? [];
    if (is_array($products) && $products) {
        foreach ($products as $i => $row) {
            if (!is_array($row)) {
                continue;
            }
            $productName = trim((string) ($row['productName'] ?? $row['label'] ?? ''));
            $model = trim((string) ($row['label'] ?? ''));
            $qty = trim((string) ($row['qty'] ?? ''));
            $lines[] = ($i + 1) . '. ' . ($productName !== '' ? $productName : 'Ürün');
            if ($model !== '') {
                $lines[] = '   Model: ' . $model . ($qty !== '' ? ' | Miktar: ' . $qty : '');
            }
        }
    } else {
        $lines[] = '(Ürün listesi gönderilmedi)';
    }

    $lines[] = '';
    $lines[] = 'Gönderim: ' . date('d.m.Y H:i:s');
    $lines[] = 'IP: ' . ($_SERVER['REMOTE_ADDR'] ?? '—');

    return [$subject, implode("\n", $lines), $email];
}

function normalizeReplyTo(string $replyTo, array $config): string
{
    if ($replyTo !== '' && filter_var($replyTo, FILTER_VALIDATE_EMAIL)) {
        return $replyTo;
    }
    return (string) ($config['mail_to'] ?? 'info@abralion.com');
}

function sendMail(array $config, string $to, string $subject, string $body, string $replyTo): void
{
    $from = (string) ($config['mail_from'] ?? '');
    $fromName = (string) ($config['mail_from_name'] ?? 'Abralion');
    if ($from === '' || !filter_var($from, FILTER_VALIDATE_EMAIL)) {
        throw new RuntimeException('Geçersiz gönderen adresi.');
    }

    if (!empty($config['use_smtp'])) {
        smtpSend($config, $to, $subject, $body, $replyTo, $from, $fromName);
        return;
    }

    $headers = implode("\r\n", [
        'MIME-Version: 1.0',
        'Content-Type: text/plain; charset=UTF-8',
        'From: ' . encodeAddress($fromName, $from),
        'Reply-To: ' . $replyTo,
        'X-Mailer: Abralion-Forms',
    ]);

    if (!@mail($to, encodeHeader($subject), $body, $headers)) {
        throw new RuntimeException('mail() başarısız.');
    }
}

function smtpSend(
    array $config,
    string $to,
    string $subject,
    string $body,
    string $replyTo,
    string $from,
    string $fromName
): void {
    $host = (string) ($config['smtp_host'] ?? '');
    $port = (int) ($config['smtp_port'] ?? 465);
    $secure = (string) ($config['smtp_secure'] ?? 'ssl');
    $user = (string) ($config['smtp_user'] ?? '');
    $pass = (string) ($config['smtp_pass'] ?? '');

    if ($host === '' || $user === '' || $pass === '' || str_contains($pass, 'BURAYA_')) {
        throw new RuntimeException('SMTP ayarları eksik.');
    }

    $ehloHost = 'abralion.com';
    if (str_contains($from, '@')) {
        $ehloHost = substr($from, strpos($from, '@') + 1);
    }

    $remote = ($secure === 'ssl' ? 'ssl://' : '') . $host . ':' . $port;
    $socket = @stream_socket_client($remote, $errno, $errstr, 20);
    if (!$socket) {
        throw new RuntimeException('SMTP bağlantısı kurulamadı: ' . $errstr);
    }

    stream_set_timeout($socket, 20);
    expectLine($socket, [220]);
    cmd($socket, 'EHLO ' . $ehloHost, [250]);

    if ($secure === 'tls') {
        cmd($socket, 'STARTTLS', [220]);
        if (!stream_socket_enable_crypto($socket, true, STREAM_CRYPTO_METHOD_TLS_CLIENT)) {
            throw new RuntimeException('STARTTLS başarısız.');
        }
        cmd($socket, 'EHLO ' . $ehloHost, [250]);
    }

    cmd($socket, 'AUTH LOGIN', [334]);
    cmd($socket, base64_encode($user), [334]);
    cmd($socket, base64_encode($pass), [235]);

    cmd($socket, 'MAIL FROM:<' . $from . '>', [250]);
    cmd($socket, 'RCPT TO:<' . $to . '>', [250, 251]);
    cmd($socket, 'DATA', [354]);

    $message = implode("\r\n", [
        'Date: ' . date('r'),
        'To: <' . $to . '>',
        'From: ' . encodeAddress($fromName, $from),
        'Reply-To: <' . $replyTo . '>',
        'Subject: ' . encodeHeader($subject),
        'MIME-Version: 1.0',
        'Content-Type: text/plain; charset=UTF-8',
        'Content-Transfer-Encoding: 8bit',
        '',
        $body,
        '.',
    ]);

    fwrite($socket, $message . "\r\n");
    expectLine($socket, [250]);
    cmd($socket, 'QUIT', [221]);
    fclose($socket);
}

function cmd($socket, string $command, array $okCodes): string
{
    fwrite($socket, $command . "\r\n");
    return expectLine($socket, $okCodes);
}

function expectLine($socket, array $okCodes): string
{
    $line = '';
    while ($chunk = fgets($socket, 515)) {
        $line = $chunk;
        if (isset($chunk[3]) && $chunk[3] === ' ') {
            break;
        }
    }
    $code = (int) substr($line, 0, 3);
    if (!in_array($code, $okCodes, true)) {
        throw new RuntimeException('SMTP hatası: ' . trim($line));
    }
    return $line;
}

function encodeAddress(string $name, string $email): string
{
    $safeName = str_replace(['"', "\r", "\n"], '', $name);
    return sprintf('"%s" <%s>', $safeName, $email);
}

function encodeHeader(string $text): string
{
    if (function_exists('mb_encode_mimeheader')) {
        return mb_encode_mimeheader($text, 'UTF-8', 'B', "\r\n");
    }
    return $text;
}
