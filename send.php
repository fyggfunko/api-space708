<?php
declare(strict_types=1);

// Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID on the server.
// Do not commit the bot token or chat id.

function telegram_notify_lead(array $lead): bool
{
    $token = getenv('TELEGRAM_BOT_TOKEN') ?: '';
    $chatId = getenv('TELEGRAM_CHAT_ID') ?: '';
    if ($token === '' || $chatId === '' || !function_exists('curl_init')) {
        return false;
    }

    $escape = static function (string $value): string {
        return htmlspecialchars($value, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');
    };
    $lines = [
        '<b>Nouvelle demande</b>',
        'Prénom: ' . $escape((string) ($lead['first_name'] ?? '')),
        'Nom: ' . $escape((string) ($lead['last_name'] ?? '')),
        'E-mail: ' . $escape((string) ($lead['email'] ?? '')),
        'Téléphone: ' . $escape((string) ($lead['phone'] ?? '')),
        'Pays: ' . $escape((string) ($lead['country_code'] ?? '')),
        'Langue: ' . $escape((string) ($lead['language'] ?? '')),
        'IP: ' . $escape((string) ($lead['ip'] ?? '')),
    ];

    $curl = curl_init('https://api.telegram.org/bot' . $token . '/sendMessage');
    curl_setopt_array($curl, [
        CURLOPT_POST => true,
        CURLOPT_RETURNTRANSFER => true,
        CURLOPT_HTTPHEADER => ['Content-Type: application/json'],
        CURLOPT_POSTFIELDS => json_encode([
            'chat_id' => $chatId,
            'text' => implode("\n", $lines),
            'parse_mode' => 'HTML',
            'disable_web_page_preview' => true,
        ], JSON_UNESCAPED_UNICODE),
        CURLOPT_CONNECTTIMEOUT => 5,
        CURLOPT_TIMEOUT => 15,
        CURLOPT_SSL_VERIFYPEER => true,
        CURLOPT_SSL_VERIFYHOST => 2,
        CURLOPT_FOLLOWLOCATION => false,
    ]);
    $response = curl_exec($curl);
    $code = (int) curl_getinfo($curl, CURLINFO_HTTP_CODE);
    $networkError = curl_errno($curl);
    curl_close($curl);
    if ($networkError || !is_string($response) || $code < 200 || $code >= 300) {
        return false;
    }
    $result = json_decode($response, true);
    return is_array($result) && !empty($result['ok']);
}

if (PHP_SAPI !== 'cli' && realpath($_SERVER['SCRIPT_FILENAME'] ?? '') === __FILE__) {
    http_response_code(410);
    header('Content-Type: text/plain; charset=utf-8');
    echo 'Use the form endpoint.';
}
