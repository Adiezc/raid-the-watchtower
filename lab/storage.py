"""SQLite storage and immutable-on-reset exported mission evidence."""

import hashlib
import json
import sqlite3
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def now():
    return datetime.now(timezone.utc).isoformat(timespec='microseconds')


def source_hash():
    digest = hashlib.sha256()
    paths = [ROOT / 'server.py'] + sorted((ROOT / 'lab').glob('*.py')) + sorted((ROOT / 'fixtures').glob('*.json'))
    for path in paths:
        digest.update(str(path.relative_to(ROOT)).encode())
        digest.update(path.read_bytes())
    return digest.hexdigest()


class Store:
    def __init__(self, path, evidence_root=None):
        self.path = Path(path).resolve()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.evidence_root = Path(evidence_root or ROOT / 'evidence').resolve()
        self.lock = threading.RLock()
        self.conn = sqlite3.connect(str(self.path), check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript('''
          CREATE TABLE IF NOT EXISTS accounts (id TEXT PRIMARY KEY, token TEXT UNIQUE, payload TEXT);
          CREATE TABLE IF NOT EXISTS dossiers (id INTEGER PRIMARY KEY, payload TEXT);
          CREATE TABLE IF NOT EXISTS integration (id TEXT PRIMARY KEY, credential TEXT, active INTEGER);
          CREATE TABLE IF NOT EXISTS events (id TEXT PRIMARY KEY, integration_id TEXT, message_id TEXT, payload TEXT, at TEXT);
          CREATE TABLE IF NOT EXISTS metadata (key TEXT PRIMARY KEY, value TEXT);
          CREATE TABLE IF NOT EXISTS request_logs (id TEXT PRIMARY KEY, run_id TEXT, payload TEXT);
          CREATE TABLE IF NOT EXISTS evidence (id TEXT PRIMARY KEY, run_id TEXT, payload TEXT);
        ''')
        self.conn.commit()
        self.fixture = json.loads((ROOT / 'fixtures/story.json').read_text())
        if not self.get('run_id'):
            self.reset()

    def close(self):
        self.conn.close()

    def get(self, key, default=None):
        with self.lock:
            row = self.conn.execute('SELECT value FROM metadata WHERE key=?', (key,)).fetchone()
            return json.loads(row['value']) if row else default

    def set(self, key, value):
        with self.lock:
            self.conn.execute('INSERT OR REPLACE INTO metadata(key,value) VALUES (?,?)', (key, json.dumps(value)))
            self.conn.commit()

    def touch(self):
        self.set('state_version', self.get('state_version', 0) + 1)

    def reset(self):
        with self.lock:
            for table in ('accounts', 'dossiers', 'integration', 'events', 'metadata'):
                self.conn.execute('DELETE FROM ' + table)
            for account in self.fixture['accounts']:
                self.conn.execute('INSERT INTO accounts VALUES (?,?,?)', (account['id'], account['token'], json.dumps(account)))
            for dossier in self.fixture['dossiers']:
                self.conn.execute('INSERT INTO dossiers VALUES (?,?)', (dossier['id'], json.dumps(dossier)))
            integration = self.fixture['integration']
            self.conn.execute('INSERT INTO integration VALUES (?,?,1)', (integration['id'], integration['credential']))
            event = dict(self.fixture['seed_event'])
            self.conn.execute('INSERT INTO events VALUES (?,?,?,?,?)', (event['id'], event['integration_id'], event['message_id'], json.dumps(event), now()))
            self.conn.commit()
            self.set('run_id', 'run-' + uuid.uuid4().hex[:12])
            self.set('created_at', now())
            self.set('notes', {'observation': '', 'hypothesis': ''})
            self.set('state_version', 0)
            self.set('verification', None)
            self.set('declaration', None)
            self.set('assistance', [])
            self.set('launch_history', [])
        return self.get('run_id')

    def account(self, token):
        with self.lock:
            row = self.conn.execute('SELECT payload FROM accounts WHERE token=?', (token,)).fetchone()
            return json.loads(row['payload']) if row else None

    def dossiers(self):
        with self.lock:
            return [json.loads(row['payload']) for row in self.conn.execute('SELECT payload FROM dossiers ORDER BY id')]

    def dossier(self, dossier_id):
        with self.lock:
            row = self.conn.execute('SELECT payload FROM dossiers WHERE id=?', (dossier_id,)).fetchone()
            return json.loads(row['payload']) if row else None

    def collector_status(self):
        with self.lock:
            row = self.conn.execute('SELECT id,active FROM integration').fetchone()
            count = self.conn.execute('SELECT COUNT(*) AS n FROM events').fetchone()['n']
            last = self.conn.execute('SELECT payload,at FROM events ORDER BY at DESC LIMIT 1').fetchone()
            return {'active': bool(row['active']), 'event_count': count, 'integration_id': row['id'],
                    'last_event': dict(json.loads(last['payload']), at=last['at']) if last else None}

    def revoke(self):
        with self.lock:
            self.conn.execute('UPDATE integration SET active=0')
            self.conn.commit()
            self.touch()
            return self.collector_status()

    def collector_credential(self, token):
        with self.lock:
            return self.conn.execute('SELECT id,active FROM integration WHERE credential=?', (token,)).fetchone()

    def collect(self, token, message_id):
        with self.lock:
            integration = self.collector_credential(token)
            if not integration or not integration['active']:
                return None
            event_id = 'event-' + uuid.uuid4().hex[:12]
            message = next(item for item in self.fixture['messages'] if item['id'] == message_id)
            event = {'id': event_id, 'integration_id': integration['id'], 'message_id': message_id, 'text': message['text']}
            self.conn.execute('INSERT INTO events VALUES (?,?,?,?,?)', (event_id, integration['id'], message_id, json.dumps(event), now()))
            self.conn.commit()
            self.touch()
            return event

    def log(self, item):
        with self.lock:
            self.conn.execute('INSERT INTO request_logs VALUES (?,?,?)', (item['request_id'], item['run_id'], json.dumps(item)))
            self.conn.commit()

    def request_log(self, request_id):
        with self.lock:
            row = self.conn.execute('SELECT payload FROM request_logs WHERE id=? AND run_id=?', (request_id, self.get('run_id'))).fetchone()
            return json.loads(row['payload']) if row else None

    def evidence(self):
        with self.lock:
            return [json.loads(row['payload']) for row in self.conn.execute('SELECT payload FROM evidence WHERE run_id=? ORDER BY id', (self.get('run_id'),))]

    def export(self, kind, label, contents, mode, actor, runtime_hash):
        evidence_id = 'evidence-' + uuid.uuid4().hex[:12]
        run_id = self.get('run_id')
        folder = self.evidence_root / run_id
        folder.mkdir(parents=True, exist_ok=True)
        item = {'id': evidence_id, 'label': label, 'kind': kind, 'run_id': run_id, 'at': now(),
                'source_hash': source_hash(), 'runtime_source_hash': runtime_hash, 'mode': mode, 'actor': actor,
                'contents': contents}
        encoded = json.dumps(item, indent=2, ensure_ascii=False).encode('utf-8')
        path = folder / (evidence_id + '.json')
        path.write_bytes(encoded)
        item_meta = {key: item[key] for key in ('id', 'label', 'kind', 'run_id', 'at')}
        item_meta['path'] = str(path.relative_to(self.evidence_root.parent))
        item_meta['sha256'] = hashlib.sha256(encoded).hexdigest()
        with self.lock:
            self.conn.execute('INSERT INTO evidence VALUES (?,?,?)', (evidence_id, run_id, json.dumps(item_meta)))
            self.conn.commit()
            self.touch()
        return item_meta
