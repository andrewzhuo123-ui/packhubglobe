"""Exercise the real endpoint with a fake mail transport. Pass a PHP CLI command as arguments."""
import base64
import json
from pathlib import Path
import subprocess
import sys
import uuid

source = Path('request-quote/send.php').read_text().removeprefix('<?php')
valid = dict(name='Website test', email='buyer@example.com', product='Paper boxes', quantity='500', country='US', consent='on', details='Line one\nLine two')
cases = [
    ('get', {}, {}, 405, False),
    ('required', {'REQUEST_METHOD': 'POST'}, {}, 422, False),
    ('bad email', {}, dict(email='invalid'), 422, False),
    ('header injection', {}, dict(email='a@example.com\r\nBcc: a@example.com'), 422, False),
    ('array field', {}, dict(name=['bad']), 422, False),
    ('consent', {}, dict(consent=''), 422, False),
    ('honeypot', {}, dict(website='spam'), 422, False),
    ('foreign origin', {'HTTP_ORIGIN': 'https://example.com'}, {}, 403, False),
    ('oversized', {'CONTENT_LENGTH': '40000'}, {}, 413, False),
    ('mail failure', {}, {}, 503, False),
    ('success', {}, {}, 200, True),
    ('cooldown', {}, {}, 429, False),
]
for name, server_patch, patch, status, ok in cases:
    server = dict(REQUEST_METHOD='POST', REMOTE_ADDR=str(uuid.uuid4()), HTTP_ORIGIN='https://www.packhubglobe.com')
    server.update(server_patch)
    if name == 'get':
        server['REQUEST_METHOD'] = 'GET'
    post = {} if name == 'required' else valid | patch
    payload = base64.b64encode(json.dumps(dict(server=server, post=post)).encode()).decode()
    code = '''namespace EnquiryTest;
function mail($to, $subject, $body, $headers) {
 if ($to !== 'andrew@packhubglobe.com' || $headers['Reply-To'] !== 'buyer@example.com' || strpos(base64_decode($body), "Line one\\nLine two") === false) throw new \\Exception('Invalid mail');
 return MAIL_OK;
}
$p=json_decode(base64_decode('PAYLOAD'),true); $_SERVER=$p['server']; $_POST=$p['post'];
if (!is_dir(sys_get_temp_dir())) mkdir(sys_get_temp_dir(), 0700, true);
register_shutdown_function(function(){echo "\\n".http_response_code();});
'''.replace('PAYLOAD', payload).replace('MAIL_OK', 'false' if name == 'mail failure' else 'true')
    if name == 'cooldown':
        code += "file_put_contents(sys_get_temp_dir().'/phg-enquiry-'.hash('sha256',$_SERVER['REMOTE_ADDR']), (string)time());"
    result = subprocess.run((sys.argv[1:] or ['php']) + ['-r', code + source], capture_output=True, text=True, check=True)
    body, actual_status = result.stdout.strip().rsplit('\n', 1)
    assert int(actual_status) == status, (name, result.stdout, result.stderr)
    assert json.loads(body)['ok'] is ok, (name, body)
    print('PASS', name)
