#!/usr/bin/env python3
"""Run the fictional Watchtower lab on this computer only."""

import argparse
import json
import re
import threading
import uuid
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

from lab import policy
from lab.outcomes import derive_outcome
from lab.storage import ROOT, Store, now, source_hash

ANALYST_TOKEN = 'analyst-demo-token'
OPERATOR_TOKEN = 'watchtower-warden-demo'
COLLECTOR_TOKEN = 'raid-companion-demo-key'
STATIC = {'/': ('index.html', 'text/html; charset=utf-8'), '/index.html': ('index.html', 'text/html; charset=utf-8'),
          '/styles.css': ('styles.css', 'text/css; charset=utf-8'), '/app.js': ('app.js', 'text/javascript; charset=utf-8'),
          '/watchtower.svg': ('watchtower.svg', 'image/svg+xml'), '/favicon.ico': ('watchtower.svg', 'image/svg+xml')}


class LabServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, address, store, training_vulnerable):
        self.store = store
        self.training_vulnerable = training_vulnerable
        self.mode = 'training-vulnerable' if training_vulnerable else 'protected'
        self.runtime_source_hash = source_hash()
        self.verify_lock = threading.Lock()
        super().__init__(address, Handler)
        history = store.get('launch_history', [])
        history.append({'at': now(), 'mode': self.mode, 'source_hash': self.runtime_source_hash,
                        'address': 'http://127.0.0.1:%d/' % self.server_port})
        store.set('launch_history', history)

    def probe(self, method, path, token, body=None):
        headers = {'Authorization': 'Bearer ' + token, 'Content-Type': 'application/json'}
        data = json.dumps(body).encode() if body is not None else None
        req = Request('http://127.0.0.1:%d%s' % (self.server_port, path), data=data, headers=headers, method=method)
        try:
            with urlopen(req, timeout=5) as response:
                return response.status, json.loads(response.read())
        except HTTPError as error:
            return error.code, json.loads(error.read())
        except (URLError, OSError, ValueError) as error:
            return 0, {'error': 'Local verification request failed: ' + str(error)}

    def verify(self):
        with self.verify_lock:
            checks = []
            probe_records = []
            for key, label, path, expected in [
                ('original', 'Original restricted file is blocked', '/api/dossiers/103', 403),
                ('variant', 'Related restricted file is blocked', '/api/dossiers/104', 403),
                ('authorised', 'Your permitted file still opens', '/api/dossiers/101', 200),
                ('filtered-list', 'Your file list contains only permitted files', '/api/dossiers', 200)]:
                status, response = self.probe('GET', path, ANALYST_TOKEN)
                passed = status == expected
                if key in ('original', 'variant'):
                    passed = passed and 'dossier' not in response
                elif key == 'authorised':
                    passed = passed and response.get('dossier', {}).get('id') == 101
                else:
                    passed = passed and {item['id'] for item in response.get('items', [])} == {101, 102}
                checks.append({'key': key, 'label': label, 'passed': passed, 'status': status,
                               'explanation': 'Expected HTTP %d; observed HTTP %d.' % (expected, status)})
                probe_records.append({'method': 'GET', 'path': path, 'status': status, 'response': response})
            before = self.store.collector_status()
            collector_probe_at = now()
            status, response = self.probe('POST', '/api/collector/events', COLLECTOR_TOKEN, {'message_id': 'message-raid-joke'})
            after = self.store.collector_status()
            passed = status in (401, 403) and before['event_count'] == after['event_count'] and not after['active']
            checks.append({'key': 'collector', 'label': 'New collection is rejected and old records remain', 'passed': passed,
                           'status': status, 'explanation': 'Event count before: %d. After: %d. Collector active: %s.' %
                           (before['event_count'], after['event_count'], str(after['active']).lower())})
            probe_records.append({'method': 'POST', 'path': '/api/collector/events', 'status': status, 'response': response,
                                  'before': before, 'after': after, 'at': collector_probe_at})
            active_hash = source_hash()
            fresh = active_hash == self.runtime_source_hash
            checks.append({'key': 'source-fresh', 'label': 'Running code matches the saved source', 'passed': fresh,
                           'status': 200 if fresh else 409,
                           'explanation': 'Running code matches the saved source.' if fresh else 'Source changed after launch. Restart the lab with the same database, then verify again.'})
            result = {'checks': checks, 'verified_at': now(), 'collector_probe_at': collector_probe_at,
                      'run_id': self.store.get('run_id'), 'mode': self.mode, 'source_hash': active_hash,
                      'defence_attempted': bool(policy.PROTECTED_IMPLEMENTED and not self.training_vulnerable),
                      'runtime_source_hash': self.runtime_source_hash, 'state_version': self.store.get('state_version'),
                      'probes': probe_records}
            result['outcome'] = derive_outcome(self.store.get('notes'), self.store.evidence(), result, self.store.get('declaration'))
            self.store.set('verification', result)
            folder = self.store.evidence_root / result['run_id']
            folder.mkdir(parents=True, exist_ok=True)
            (folder / ('verification-' + uuid.uuid4().hex[:12] + '.json')).write_text(json.dumps(result, indent=2))
            return result


class Handler(BaseHTTPRequestHandler):
    protocol_version = 'HTTP/1.1'

    def log_message(self, format_string, *args):
        pass

    def do_GET(self):
        self.handle_request('GET')

    def do_POST(self):
        self.handle_request('POST')

    def do_OPTIONS(self):
        self.handle_request('OPTIONS')

    def token(self):
        value = self.headers.get('Authorization', '')
        return value[7:] if value.startswith('Bearer ') else ''

    def answer(self, status, payload):
        payload = dict(payload, request_id=self.request_id)
        encoded = json.dumps(payload, ensure_ascii=False).encode('utf-8')
        actor = self.account['id'] if self.account else ('collector' if self.server.store.collector_credential(self.token()) else 'anonymous')
        credential_alias = {'analyst': 'analyst-demo-token', 'operator': 'watchtower-warden-demo',
                            'collector': 'raid-companion-demo-key'}.get(actor, None)
        self.server.store.log({'request_id': self.request_id, 'run_id': self.server.store.get('run_id'), 'at': now(),
                               'mode': self.server.mode, 'source_hash': source_hash(), 'runtime_source_hash': self.server.runtime_source_hash,
                               'actor': actor, 'request': {'method': self.command, 'path': self.path, 'body': self.body,
                               'synthetic_credential_alias': credential_alias},
                               'response': {'status': status, 'body': payload}})
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.common_headers(len(encoded))
        self.end_headers()
        self.wfile.write(encoded)

    def common_headers(self, length):
        self.send_header('Content-Length', str(length))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Referrer-Policy', 'no-referrer')
        self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'")

    def require_account(self, role=None):
        if not self.account:
            self.answer(401, {'error': 'Use the supplied account pass to sign in.'})
            return False
        if role and self.account['role'] != role:
            text = 'This control is available only to the Watchtower operator.' if role == 'operator' else 'Use the training analyst account for this investigation action.'
            self.answer(403, {'error': text})
            return False
        return True

    def handle_request(self, method):
        self.request_id = 'request-' + uuid.uuid4().hex[:12]
        self.body = None
        self.account = self.server.store.account(self.token())
        host = self.headers.get('Host', '')
        if host not in ('127.0.0.1:%d' % self.server.server_port, 'localhost:%d' % self.server.server_port):
            self.answer(400, {'error': 'Use the local lab address shown at launch.'})
            return
        origin = self.headers.get('Origin')
        if origin and origin not in ('http://127.0.0.1:%d' % self.server.server_port, 'http://localhost:%d' % self.server.server_port):
            self.answer(403, {'error': 'Requests must come from this local lab.'})
            return
        path = urlsplit(self.path).path
        if method == 'POST':
            try:
                length = int(self.headers.get('Content-Length', '0'))
                if length < 0 or length > 32768:
                    self.answer(413, {'error': 'The submitted note is too large.'})
                    return
                raw = self.rfile.read(length)
                self.body = json.loads(raw) if raw else {}
                if not isinstance(self.body, dict):
                    raise ValueError('Object required')
            except (ValueError, UnicodeDecodeError):
                self.answer(400, {'error': 'Submit a JSON object.'})
                return
        if method == 'GET' and path in STATIC and not urlsplit(self.path).query:
            name, content_type = STATIC[path]
            file_path = ROOT / 'web' / name
            if not file_path.is_file():
                self.answer(404, {'error': 'The browser view is not installed yet.'})
                return
            encoded = file_path.read_bytes()
            self.send_response(200)
            self.send_header('Content-Type', content_type)
            self.common_headers(len(encoded))
            self.end_headers()
            self.wfile.write(encoded)
            return
        if method == 'GET' and path == '/api/session':
            self.answer(200, {'mode': self.server.mode, 'build_stage': 'baseline' if not policy.PROTECTED_IMPLEMENTED else 'defended',
                              'run_id': self.server.store.get('run_id'), 'analyst': {'token': ANALYST_TOKEN,
                              'display_name': 'Training analyst', 'allowed_dossier_ids': [101, 102]}})
        elif method == 'GET' and path == '/api/brief':
            self.answer(200, {key: self.server.store.fixture[key] for key in ('premise', 'messages', 'slide', 'glossary')})
        elif method == 'GET' and path == '/api/dossiers':
            if not self.require_account():
                return
            items = [item for item in self.server.store.dossiers() if item['workspace'] == self.account['workspace'] or self.account['role'] == 'operator']
            self.answer(200, {'items': [{key: item[key] for key in ('id', 'title', 'summary', 'workspace')} for item in items]})
        elif method == 'GET' and re.fullmatch(r'/api/dossiers/[0-9]+', path):
            if not self.require_account():
                return
            dossier = self.server.store.dossier(int(path.rsplit('/', 1)[1]))
            if not dossier:
                self.answer(404, {'error': 'That file does not exist in the synthetic lab.'})
            elif not policy.can_read_dossier(self.account, dossier, self.server.training_vulnerable):
                self.answer(403, {'error': 'Your account does not have permission to read this file.'})
            else:
                self.answer(200, {'dossier': dossier})
        elif method == 'GET' and path == '/api/mission/status':
            if not self.require_account():
                return
            verification = self.server.store.get('verification')
            fresh = verification and verification['run_id'] == self.server.store.get('run_id') and verification['mode'] == self.server.mode and verification['source_hash'] == source_hash() and verification['runtime_source_hash'] == self.server.runtime_source_hash and verification['state_version'] == self.server.store.get('state_version')
            if not fresh:
                verification = None
            notes = self.server.store.get('notes')
            evidence = self.server.store.evidence()
            self.answer(200, {'run_id': self.server.store.get('run_id'), 'notes': notes, 'evidence': evidence,
                              'assistance': self.server.store.get('assistance', []),
                              'verification': verification, 'outcome': derive_outcome(notes, evidence, verification, self.server.store.get('declaration'))})
        elif method == 'POST' and path == '/api/notes':
            if not self.require_account('analyst'):
                return
            if not all(isinstance(self.body.get(key, ''), str) and len(self.body.get(key, '')) <= 8000 for key in ('observation', 'hypothesis')):
                self.answer(400, {'error': 'Notes must be text of 8,000 characters or fewer.'})
                return
            notes = {key: self.body.get(key, '').strip() for key in ('observation', 'hypothesis')}
            self.server.store.set('notes', notes)
            self.server.store.touch()
            self.answer(200, {'notes': notes})
        elif method == 'POST' and path == '/api/mission/assistance':
            if not self.require_account('analyst'):
                return
            level = self.body.get('level')
            if self.body.get('kind') != 'hint' or type(level) is not int or not 1 <= level <= 4 or set(self.body) != {'kind', 'level'}:
                self.answer(400, {'error': 'Choose one of the four optional hint levels.'})
                return
            assistance = self.server.store.get('assistance', [])
            assistance.append({'kind': 'hint', 'level': level, 'at': now(), 'actor': self.account['id']})
            self.server.store.set('assistance', assistance)
            self.answer(200, {'assistance': assistance})
        elif method == 'POST' and path == '/api/evidence':
            if not self.require_account('analyst'):
                return
            if self.body.get('kind') == 'clue':
                fixture = self.server.store.fixture
                message = next(item for item in fixture['messages'] if item['id'] == 'message-raid-joke')
                saved = self.server.store.export('clue', 'Private joke and matching sales slide', {'message': message, 'slide': fixture['slide']}, self.server.mode, self.account['id'], self.server.runtime_source_hash)
            elif isinstance(self.body.get('request_id'), str):
                log = self.server.store.request_log(self.body['request_id'])
                if not log or log['actor'] != self.account['id']:
                    self.answer(404, {'error': 'Choose a request made by your account during this mission.'})
                    return
                dossier = log['response']['body'].get('dossier', {})
                kind = 'restricted-dossier' if log['response']['status'] == 200 and dossier.get('id') in (103, 104) and dossier.get('workspace') not in (None, self.account['workspace']) else 'request'
                label = 'Restricted dossier %s response' % dossier['id'] if kind == 'restricted-dossier' else '%s %s response' % (log['request']['method'], log['request']['path'])
                saved = self.server.store.export(kind, label, log, self.server.mode, self.account['id'], self.server.runtime_source_hash)
            else:
                self.answer(400, {'error': 'Choose the opening clue or a real request ID to preserve.'})
                return
            self.answer(201, {'saved': saved})
        elif method == 'POST' and path == '/api/mission/declaration':
            if not self.require_account('analyst'):
                return
            if self.body != {'victory': True}:
                self.answer(400, {'error': 'This action records an explicit victory declaration only.'})
                return
            declaration = {'victory': True, 'at': now(), 'actor': self.account['id']}
            self.server.store.set('declaration', declaration)
            self.server.store.touch()
            self.answer(200, {'declaration': declaration})
        elif method == 'GET' and path == '/api/collector/status':
            if self.require_account('operator'):
                self.answer(200, self.server.store.collector_status())
        elif method == 'POST' and path == '/api/collector/revoke':
            if self.require_account('operator'):
                self.answer(200, self.server.store.revoke())
        elif method == 'POST' and path == '/api/collector/events':
            integration = self.server.store.collector_credential(self.token())
            if not integration:
                self.answer(401, {'error': 'The collector pass is missing or invalid.'})
            elif not integration['active']:
                self.answer(403, {'error': 'This collector pass has been revoked. No event was stored.'})
            elif set(self.body) - {'message_id'} or self.body.get('message_id', 'message-raid-joke') != 'message-raid-joke':
                self.answer(400, {'error': 'Only the supplied synthetic training message may be collected.'})
            else:
                event = self.server.store.collect(self.token(), self.body.get('message_id', 'message-raid-joke'))
                if event is None:
                    self.answer(403, {'error': 'This collector pass has been revoked. No event was stored.'})
                else:
                    self.answer(201, {'accepted': True, 'event_id': event['id'], 'event_count': self.server.store.collector_status()['event_count']})
        elif method == 'POST' and path == '/api/collector/simulate':
            if not self.require_account('operator'):
                return
            status, response = self.server.probe('POST', '/api/collector/events', COLLECTOR_TOKEN, {'message_id': 'message-raid-joke'})
            self.answer(200, {'accepted': status == 201, 'status': status, 'event_count': self.server.store.collector_status()['event_count'], 'collector_response': response})
        elif method == 'POST' and path == '/api/mission/verify':
            if self.require_account('operator'):
                self.answer(200, self.server.verify())
        else:
            self.answer(404, {'error': 'That route is not part of this local lab.'})


def main():
    parser = argparse.ArgumentParser(description='A fictional cybersecurity exercise, running on this computer only.')
    parser.add_argument('--training-vulnerable', action='store_true', help='Explicitly enable the intentional dossier permission flaw.')
    parser.add_argument('--reset', action='store_true', help='Restore synthetic fixtures, start a new run and exit. Exported evidence is kept.')
    parser.add_argument('--db', type=Path, default=ROOT / 'var/watchtower.sqlite3')
    parser.add_argument('--port', type=int, default=8765)
    parser.add_argument('--evidence-dir', type=Path, default=ROOT / 'evidence')
    parser.add_argument('--open-browser', action='store_true', help='Open the local lab in your default browser.')
    args = parser.parse_args()
    if not 0 <= args.port <= 65535:
        parser.error('Choose a valid local port number.')
    if not args.reset and not args.training_vulnerable and not policy.PROTECTED_IMPLEMENTED:
        parser.error('The blue defence has not been implemented yet. The baseline requires --training-vulnerable.')
    store = Store(args.db, args.evidence_dir)
    if args.reset:
        run_id = store.reset()
        print('Synthetic fixtures restored. New mission: %s. Exported evidence was preserved.' % run_id)
        store.close()
        return
    server = LabServer(('127.0.0.1', args.port), store, args.training_vulnerable)
    address = 'http://127.0.0.1:%d/' % server.server_port
    print('Raid the Watchtower: %s' % address, flush=True)
    print('Mode: %s. All records are fictional. Press Control+C to stop.' % server.mode, flush=True)
    if args.open_browser:
        threading.Timer(0.4, lambda: webbrowser.open(address)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\nLocal lab stopped.')
    finally:
        server.server_close()
        store.close()


if __name__ == '__main__':
    main()
