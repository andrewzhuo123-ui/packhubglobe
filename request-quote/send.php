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
if ((int) ($_SERVER['CONTENT_LENGTH'] ?? 0) > 11 * 1024 * 1024) {
    respond(413, false, 'Attachments must total 10 MB or less.');
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

$attachments = [];
$totalSize = 0;
if (isset($_FILES['attachments'])) {
    $upload = $_FILES['attachments'];
    foreach (['name', 'tmp_name', 'error'] as $key) {
        if (!isset($upload[$key]) || !is_array($upload[$key])) {
            respond(422, false, 'Please select the attachments again.');
        }
    }
    if (count($upload['name']) > 5) {
        respond(422, false, 'Please attach no more than 5 files.');
    }
    foreach ($upload['name'] as $index => $name) {
        $error = $upload['error'][$index] ?? null;
        if ($error === UPLOAD_ERR_NO_FILE) continue;
        if ($error !== UPLOAD_ERR_OK) {
            respond(422, false, 'A file could not be uploaded. Each file must be 5 MB or less. Please select it again.');
        }
        $path = $upload['tmp_name'][$index] ?? null;
        if (!is_string($name) || !is_string($path) || !is_uploaded_file($path)) {
            respond(422, false, 'Please select the attachments again.');
        }
        $size = filesize($path);
        $totalSize += $size;
        if ($size === 0 || $size > 5 * 1024 * 1024 || $totalSize > 10 * 1024 * 1024) {
            respond(422, false, 'Use non-empty files up to 5 MB each and 10 MB in total.');
        }
        $extension = strtolower(pathinfo($name, PATHINFO_EXTENSION));
        $signature = file_get_contents($path, false, null, 0, 12);
        $types = [
            'jpg' => ['image/jpeg', strncmp($signature, "\xff\xd8\xff", 3) === 0],
            'jpeg' => ['image/jpeg', strncmp($signature, "\xff\xd8\xff", 3) === 0],
            'png' => ['image/png', strncmp($signature, "\x89PNG\r\n\x1a\n", 8) === 0],
            'webp' => ['image/webp', substr($signature, 0, 4) === 'RIFF' && substr($signature, 8, 4) === 'WEBP'],
            'pdf' => ['application/pdf', strncmp($signature, '%PDF-', 5) === 0],
            'ai' => ['application/postscript', strncmp($signature, '%PDF-', 5) === 0 || strncmp($signature, '%!PS', 4) === 0],
            'eps' => ['application/postscript', strncmp($signature, '%!PS', 4) === 0 || substr($signature, 0, 4) === "\xc5\xd0\xd3\xc6"],
            'psd' => ['image/vnd.adobe.photoshop', substr($signature, 0, 4) === '8BPS'],
            'zip' => ['application/zip', in_array(substr($signature, 0, 4), ["PK\x03\x04", "PK\x05\x06", "PK\x07\x08"], true)]
        ];
        if (!isset($types[$extension]) || !$types[$extension][1]) {
            respond(422, false, 'Use JPG, PNG, WebP, PDF, AI, PSD, EPS or ZIP files with the correct file extension.');
        }
        // Keep names out of raw MIME headers; uploaded files stay in PHP temporary storage.
        $filename = basename(str_replace('\\', '/', $name));
        $attachments[] = ['path' => $path, 'name' => $filename, 'type' => $types[$extension][0]];
    }
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
$message = chunk_split(base64_encode($body));
if ($attachments) {
    $boundary = 'phg-' . bin2hex(random_bytes(16));
    $headers['Content-Type'] = 'multipart/mixed; boundary="' . $boundary . '"';
    unset($headers['Content-Transfer-Encoding']);
    $message = '--' . $boundary . "\r\nContent-Type: text/plain; charset=UTF-8\r\nContent-Transfer-Encoding: base64\r\n\r\n" . $message;
    foreach ($attachments as $file) {
        $filename = rawurlencode($file['name']);
        $message .= '--' . $boundary . "\r\nContent-Type: " . $file['type'] . "\r\nContent-Disposition: attachment; filename*=UTF-8''" . $filename . "\r\nContent-Transfer-Encoding: base64\r\n\r\n" . chunk_split(base64_encode(file_get_contents($file['path'])));
    }
    $message .= '--' . $boundary . "--\r\n";
}
$sent = function_exists('mail') && @mail('andrew@packhubglobe.com', 'PackHubGlobe packaging enquiry', $message, $headers);
if (!$sent) {
    respond(503, false, 'Your enquiry could not be sent. Please email andrew@packhubglobe.com or contact us on WhatsApp.');
}
rewind($lock);
ftruncate($lock, 0);
fwrite($lock, (string) time());
fclose($lock);
respond(200, true, 'Your enquiry has been submitted for email delivery.');
