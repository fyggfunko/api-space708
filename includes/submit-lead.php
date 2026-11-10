<?php
declare(strict_types=1);
require_once __DIR__ . '/lead-common.php';
require_once __DIR__ . '/../send.php';
lead_session();
$lang = ($_POST['language'] ?? 'fr') === 'de' ? 'de' : 'fr';
if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') {
    header('Allow: POST');
    lead_fail($lang, 'method', 405);
}
$csrf = lead_text('csrf', 64);
if (!$csrf || !hash_equals($_SESSION['csrf'], $csrf)) lead_fail($lang, 'csrf', 403);
$submission = lead_text('submission_id', 64);
if (!$submission || !hash_equals($_SESSION['submission_id'] ?? '', $submission)) lead_fail($lang, 'csrf', 403);
if (($_SESSION['accepted_submission'] ?? '') === $submission) {
    header('Location: index3.php', true, 303);
    exit;
}
$first = lead_text('fn', 100);
$last = lead_text('ln', 100);
$email = lead_text('em', 254);
$phone = preg_replace('/[\s().-]/', '', lead_text('phone', 40));
$country = lead_text('country_code', 2);
$countries = require __DIR__ . '/countries.php';
if (!$first || !$last || !filter_var($email, FILTER_VALIDATE_EMAIL)
    || !preg_match('/^\+[1-9][0-9]{7,14}$/', $phone)
    || !isset($countries[$country]) || lead_text('consent', 1) !== '1'
    || lead_text('website') !== '') {
    lead_fail($lang, 'invalid', 422);
}
if (time() - ($_SESSION['last_attempt'] ?? 0) < 60) lead_fail($lang, 'rate', 429);
$config = require __DIR__ . '/yourleads-config.php';
$telegramReady = (getenv('TELEGRAM_BOT_TOKEN') ?: '') !== '' && (getenv('TELEGRAM_CHAT_ID') ?: '') !== '';
$crmReady = $config['token'] !== '';
if ((!$telegramReady && !$crmReady) || !function_exists('curl_init')) lead_fail($lang, 'unavailable', 503);
$_SESSION['last_attempt'] = time();
// Do not trust arbitrary Forwarded / CF headers. Configure trusted proxies at the web server.
$ip = $_SERVER['REMOTE_ADDR'] ?? '';
if (!filter_var($ip, FILTER_VALIDATE_IP)) lead_fail($lang, 'invalid', 422);
$lead = [
    'ip' => $ip,
    'country_code' => $country,
    'email' => $email,
    'first_name' => $first,
    'last_name' => $last,
    'phone' => $phone,
    'language' => $lang,
];
if ($crmReady) {
    $payload = $lead + [
        'affiliate_id' => $config['affiliate_id'],
        'password' => bin2hex(random_bytes(12)),
        'goal_type_uuid' => $config['goal_uuid'],
        'aff_sub3' => $config['funnel'],
        'is_test' => false,
    ];
    $curl = curl_init('https://yourleads.org/api/affiliates/v2/leads');
    curl_setopt_array($curl, [
        CURLOPT_POST => true, CURLOPT_RETURNTRANSFER => true,
        CURLOPT_HTTPHEADER => ['Authorization: ' . $config['token'], 'Content-Type: application/json'],
        CURLOPT_POSTFIELDS => json_encode($payload),
        CURLOPT_CONNECTTIMEOUT => 5, CURLOPT_TIMEOUT => 20,
        CURLOPT_SSL_VERIFYPEER => true, CURLOPT_SSL_VERIFYHOST => 2,
        CURLOPT_FOLLOWLOCATION => false,
    ]);
    $response = curl_exec($curl);
    $code = (int) curl_getinfo($curl, CURLINFO_HTTP_CODE);
    $networkError = curl_errno($curl);
    curl_close($curl);
    // No payload, credentials, personal details, autologin links or API response are logged.
    $result = is_string($response) ? json_decode($response, true) : null;
    if ($networkError || $response === false || $code >= 500 || ($code >= 200 && $code < 300 && !is_array($result))) {
        lead_fail($lang, 'uncertain', 502);
    }
    if (!lead_accepted($code, $result)) lead_fail($lang, 'rejected', 422);
}
if ($telegramReady && !telegram_notify_lead($lead)) lead_fail($lang, 'uncertain', 502);
$_SESSION['accepted_submission'] = $submission;
$_SESSION['lead_success'] = true;
$_SESSION['lead_success_at'] = time();
// Original local confirmation route, not the API-provided autologin URL.
header('Location: index3.php', true, 303);
exit;
