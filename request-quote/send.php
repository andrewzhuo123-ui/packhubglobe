<?php
// Fixed recipient: this endpoint cannot be used to send to arbitrary addresses.
header('Content-Type: application/json; charset=utf-8');
header('Cache-Control: no-store');

function respond($status, $ok, $message) {
    http_response_code($status);
    echo json_encode(['ok' => $ok, 'message' => $message]);
    exit;
}

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    header('Allow: POST');
    respond(405, false, 'Please submit the enquiry form.');
}
if (isset($_SERVER['HTTP_ORIGIN']) && !in_array($_SERVER['HTTP_ORIGIN'], ['https://www.packhubglobe.com', 'https://packhubglobe.com'], true)) {
    respond(403, false, 'Please submit the form from packhubglobe.com.');
}
if ((int) ($_SERVER['CONTENT_LENGTH'] ?? 0) > 32768) {
    respond(413, false, 'Your enquiry is too long. Please shorten the project details.');
}

$fields = [];
foreach (['name', 'email', 'company', 'product', 'quantity', 'country', 'size', 'unit', 'timing', 'details', 'website', 'consent'] as $key) {
    if (isset($_POST[$key]) && !is_string($_POST[$key])) {
        respond(422, false, 'Please check the form fields.');
    }
    $fields[$key] = trim($_POST[$key] ?? '');
    if (strlen($fields[$key]) > ($key === 'details' ? 20000 : 720)) {
        respond(422, false, 'Please shorten the form fields.');
    }
}
if ($fields['website'] !== '') {
    respond(422, false, 'Please leave the website field empty.');
}
foreach (['name', 'email', 'product', 'quantity', 'country', 'consent'] as $key) {
    if ($fields[$key] === '') {
        respond(422, false, 'Please complete all required fields and agree to the privacy notice.');
    }
}
if (!filter_var($fields['email'], FILTER_VALIDATE_EMAIL) || preg_match('/[\r\n]/', $fields['email'])) {
    respond(422, false, 'Please enter a valid email address.');
}

// Serialize requests per IP and allow one successful submission per minute.
$lock = @fopen(sys_get_temp_dir() . '/phg-enquiry-' . hash('sha256', $_SERVER['REMOTE_ADDR'] ?? 'unknown'), 'c+');
if (!$lock || !flock($lock, LOCK_EX)) {
    respond(503, false, 'The enquiry service is unavailable. Please email andrew@packhubglobe.com.');
}
$lastSent = (int) stream_get_contents($lock);
if ($lastSent > time() - 60) {
    header('Retry-After: 60');
    respond(429, false, 'Please wait a minute before sending another enquiry.');
}

$body = "PACKHUBGLOBE — PACKAGING REQUEST\n\n";
foreach (['name', 'email', 'company', 'product', 'quantity', 'country', 'size', 'unit', 'timing', 'details'] as $key) {
    $body .= ucfirst($key) . ': ' . ($fields[$key] ?: 'Not specified') . "\n";
}
$headers = [
    'From' => 'PackHubGlobe Website <andrew@packhubglobe.com>',
    'Reply-To' => $fields['email'],
    'MIME-Version' => '1.0',
    'Content-Type' => 'text/plain; charset=UTF-8',
    'Content-Transfer-Encoding' => 'base64'
];
$sent = function_exists('mail') && @mail('andrew@packhubglobe.com', 'PackHubGlobe packaging enquiry', chunk_split(base64_encode($body)), $headers);
if (!$sent) {
    respond(503, false, 'Your enquiry could not be sent. Please email andrew@packhubglobe.com or contact us on WhatsApp.');
}
rewind($lock);
ftruncate($lock, 0);
fwrite($lock, (string) time());
fclose($lock);
respond(200, true, 'Your enquiry has been submitted for email delivery.');
