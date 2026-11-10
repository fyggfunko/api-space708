<?php
declare(strict_types=1);
// Shared server-side session, validation and response handling.
function lead_session(): void {
    if (session_status() !== PHP_SESSION_ACTIVE) {
        session_name('kaleo_lead');
        session_start([
            'use_strict_mode' => 1,
            'cookie_httponly' => true,
            'cookie_samesite' => 'Lax',
            'cookie_secure' => !empty($_SERVER['HTTPS']) && $_SERVER['HTTPS'] !== 'off',
            'cookie_path' => '/',
        ]);
    }
    header('Cache-Control: no-store');
    if (empty($_SESSION['csrf'])) {
        $_SESSION['csrf'] = bin2hex(random_bytes(32));
    }
}
function lead_text(string $key, int $max = 200): string {
    $value = $_POST[$key] ?? '';
    if (!is_string($value)) return '';
    $value = trim($value);
    return strlen($value) <= $max ? $value : '';
}
function lead_e(string $value): string {
    return htmlspecialchars($value, ENT_QUOTES | ENT_SUBSTITUTE, 'UTF-8');
}
function lead_accepted(int $code, $result): bool {
    // Observed archive success response: {"lead_uuid": "...", "auto_login_url": "..."}.
    // Error responses can also include data.lead_uuid: never treat these as success.
    return $code >= 200 && $code < 300 && is_array($result)
        && is_string($result['lead_uuid'] ?? null) && $result['lead_uuid'] !== ''
        && empty($result['error']) && empty($result['errors']) && empty($result['errorMessage'])
        && empty($result['data']['errorMessage']);
}
function lead_fail(string $lang, string $reason, int $code): void {
    $messages = [
        'fr' => [
            'invalid' => 'Vérifiez votre nom, votre e-mail, votre téléphone au format international, votre pays et votre consentement.',
            'csrf' => 'La session a expiré. Revenez au formulaire et réessayez.',
            'rate' => 'Veuillez patienter une minute avant une nouvelle tentative.',
            'unavailable' => 'Le service est temporairement indisponible. Aucune confirmation de réception ne peut être donnée.',
            'uncertain' => 'La réception de votre demande n’a pas pu être confirmée. Elle a peut-être été reçue. Contactez-nous avant de réessayer pour éviter un doublon.',
            'rejected' => 'La demande n’a pas été acceptée par le service. Vérifiez vos coordonnées ou contactez-nous.',
            'method' => 'Utilisez le formulaire pour envoyer votre demande.',
        ],
        'de' => [
            'invalid' => 'Prüfen Sie Name, E-Mail, Telefonnummer im internationalen Format, Land und Einwilligung.',
            'csrf' => 'Die Sitzung ist abgelaufen. Öffnen Sie das Formular erneut.',
            'rate' => 'Bitte warten Sie eine Minute vor einem erneuten Versuch.',
            'unavailable' => 'Der Dienst ist vorübergehend nicht verfügbar. Der Eingang kann nicht bestätigt werden.',
            'uncertain' => 'Der Eingang konnte nicht bestätigt werden. Ihre Anfrage wurde möglicherweise bereits empfangen. Kontaktieren Sie uns vor einem erneuten Versuch, um Duplikate zu vermeiden.',
            'rejected' => 'Der Dienst hat die Anfrage nicht angenommen. Prüfen Sie Ihre Angaben oder kontaktieren Sie uns.',
            'method' => 'Bitte senden Sie Ihre Anfrage über das Formular.',
        ],
    ];
    http_response_code($code);
    header('Content-Type: text/html; charset=utf-8');
    $text = lead_e($messages[$lang][$reason]);
    $back = $lang === 'de' ? 'Zurück zum Formular' : 'Retour au formulaire';
    echo '<!doctype html><html lang="'.$lang.'"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>KALEO 1 LTD</title><body><main><h1>KALEO 1 LTD</h1><p role="alert">'.$text.'</p><p><a href="index2.php#lead-section">'.$back.'</a></p><p><a href="tel:+447412655101">+44 7412 655101</a></p></main></body></html>';
    exit;
}
