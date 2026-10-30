"""Exercise the real endpoint with a fake mail transport. Pass a PHP CLI command as arguments."""
import base64
import json
from email import policy
from email.parser import BytesParser
from pathlib import Path
import subprocess
import sys
import uuid

source = Path('request-quote/send.php').read_text().removeprefix('<?php')
valid = dict(name='Website test', email='buyer@example.com', product='Paper boxes', quantity='500', country='US', consent='on', details='Line one\nLine two')
cases = [
    ('get', {}, {}, 405, False),
    ('required', {'REQUEST_METHOD': 'POST'}, {}, 422, False),
    ('minimal brief', {}, dict(name='', quantity='', country=''), 200, True),
    ('missing requirements', {}, dict(details=''), 422, False),
    ('bad email', {}, dict(email='invalid'), 422, False),
    ('header injection', {}, dict(email='a@example.com\r\nBcc: a@example.com'), 422, False),
    ('array field', {}, dict(name=['bad']), 422, False),
    ('consent', {}, dict(consent=''), 422, False),
    ('honeypot', {}, dict(website='spam'), 422, False),
    ('foreign origin', {'HTTP_ORIGIN': 'https://example.com'}, {}, 403, False),
    ('oversized', {'CONTENT_LENGTH': '12000000'}, {}, 413, False),
    ('mail failure', {}, {}, 503, False),
    ('success', {}, {}, 200, True),
    ('context', {}, dict(source_page='/catalog/custom-corrugated-mailer-box-1600659751763/', product_reference='PHG-1600659751763'), 200, True),
    ('html source', {}, dict(source_page='/404.html'), 200, True),
    ('foreign source', {}, dict(source_page='https://example.com/private'), 422, False),
    ('source query', {}, dict(source_page='/catalog/?email=private@example.com'), 422, False),
    ('bad reference', {}, dict(product_reference='PHG-123\nBcc: test@example.com'), 422, False),
    ('cooldown', {}, {}, 429, False),
    ('attachments', {}, {}, 200, True),
    ('empty selection', {}, {}, 200, True),
    ('bad extension', {}, {}, 422, False),
    ('bad signature', {}, {}, 422, False),
    ('large file', {}, {}, 422, False),
    ('total size', {}, {}, 422, False),
    ('too many files', {}, {}, 422, False),
    ('upload error', {}, {}, 422, False),
    ('empty file', {}, {}, 422, False),
    ('not uploaded', {}, {}, 422, False),
]
for name, server_patch, patch, status, ok in cases:
    server = dict(REQUEST_METHOD='POST', REMOTE_ADDR=str(uuid.uuid4()), HTTP_ORIGIN='https://www.packhubglobe.com')
    server.update(server_patch)
    if name == 'get':
        server['REQUEST_METHOD'] = 'GET'
    post = {} if name == 'required' else valid | patch
    fixtures = []
    pdf = dict(name='参考 artwork.pdf', content=base64.b64encode(b'%PDF-1.4\nTest artwork\n%%EOF').decode())
    png = dict(name='sample.png', content='iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+jZ3cAAAAASUVORK5CYII=')
    if name == 'attachments': fixtures = [pdf, png]
    elif name == 'empty selection': fixtures = [dict(name='', error=4)]
    elif name == 'bad extension': fixtures = [pdf | dict(name='test.php')]
    elif name == 'bad signature': fixtures = [pdf | dict(name='fake.png')]
    elif name == 'large file': fixtures = [pdf | dict(size=5*1024*1024+1)]
    elif name == 'total size': fixtures = [pdf | dict(size=4*1024*1024)] * 3
    elif name == 'too many files': fixtures = [pdf] * 6
    elif name == 'upload error': fixtures = [pdf | dict(error=1)]
    elif name == 'empty file': fixtures = [pdf | dict(content='')]
    elif name == 'not uploaded': fixtures = [pdf]
    payload = base64.b64encode(json.dumps(dict(server=server, post=post, fixtures=fixtures, uploaded=name != 'not uploaded')).encode()).decode()
    code = '''namespace EnquiryTest;
ob_start();
function is_uploaded_file($path) { global $p; return $p['uploaded'] && is_file($path); }
function mail($to, $subject, $body, $headers) {
 if ($to !== 'andrew@packhubglobe.com' || $headers['Reply-To'] !== 'buyer@example.com') throw new \\Exception('Invalid mail');
 echo 'MAIL:'.base64_encode(json_encode(['body'=>$body,'headers'=>$headers]))."\\n";
 return MAIL_OK;
}
$p=json_decode(base64_decode('PAYLOAD'),true); $_SERVER=$p['server']; $_POST=$p['post'];
if (!is_dir(sys_get_temp_dir())) mkdir(sys_get_temp_dir(), 0700, true);
foreach ($p['fixtures'] as $i=>$file) {
 $path=tempnam(sys_get_temp_dir(),'phg-test-');
 $content=base64_decode($file['content']??'');
 if (isset($file['size'])) $content=str_pad($content, $file['size'], 'a');
 file_put_contents($path,$content);
 $_FILES['attachments']['name'][$i]=$file['name'];
 $_FILES['attachments']['tmp_name'][$i]=$path;
 $_FILES['attachments']['error'][$i]=$file['error']??0;
 register_shutdown_function(function()use($path){unlink($path);});
}
register_shutdown_function(function(){echo "\\n".http_response_code();});
'''.replace('PAYLOAD', payload).replace('MAIL_OK', 'false' if name == 'mail failure' else 'true')
    if name == 'cooldown':
        code += "file_put_contents(sys_get_temp_dir().'/phg-enquiry-'.hash('sha256',$_SERVER['REMOTE_ADDR']), (string)time());"
    result = subprocess.run((sys.argv[1:] or ['php']) + ['-r', code + source], capture_output=True, text=True, check=True)
    lines = result.stdout.strip().splitlines()
    mail = None
    if lines[0].startswith('MAIL:'):
        mail = json.loads(base64.b64decode(lines.pop(0)[5:]))
    assert len(lines) == 2, (name, lines, result.stderr)
    body, actual_status = lines
    if mail:
        raw = ''.join(f'{key}: {value}\r\n' for key, value in mail['headers'].items()) + '\r\n' + mail['body']
        message = BytesParser(policy=policy.default).parsebytes(raw.encode())
        text = message.get_body().get_content() if message.is_multipart() else message.get_content()
        assert 'Line one\nLine two' in text
        if name == 'context':
            assert 'Source page: /catalog/custom-corrugated-mailer-box-1600659751763/' in text
            assert 'Product reference: PHG-1600659751763' in text
        parts = list(message.iter_attachments())
        assert len(parts) == (2 if name == 'attachments' else 0)
        if parts:
            assert parts[0].get_filename() == pdf['name']
            assert parts[0].get_payload(decode=True) == base64.b64decode(pdf['content'])
            assert parts[1].get_payload(decode=True) == base64.b64decode(png['content'])
    assert int(actual_status) == status, (name, result.stdout, result.stderr)
    assert json.loads(body)['ok'] is ok, (name, body)
    print('PASS', name)
