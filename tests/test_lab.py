"""Real HTTP integration checks for the intentionally vulnerable baseline.

The source repair and protected replay checks are added during the blue round.
No baseline test asserts that the defence has already happened.
"""

import json
import subprocess
import sys
import tempfile
import threading
import unittest
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lab.outcomes import derive_outcome
from lab.storage import ROOT, Store
from server import ANALYST_TOKEN, COLLECTOR_TOKEN, OPERATOR_TOKEN, LabServer


class LabHarness(unittest.TestCase):
    TRAINING_VULNERABLE = True

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.db = Path(self.temp.name) / 'lab.sqlite3'
        self.exports = Path(self.temp.name) / 'evidence'
        self.store = Store(self.db, self.exports)
        self.start()

    def start(self):
        self.server = LabServer(('127.0.0.1', 0), self.store, self.TRAINING_VULNERABLE)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.base = 'http://127.0.0.1:%d' % self.server.server_port

    def stop(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=5)

    def tearDown(self):
        self.stop()
        self.store.close()
        self.temp.cleanup()

    def request(self, method, path, token=None, body=None, extra_headers=None):
        headers = dict(extra_headers or {})
        if token is not None:
            headers['Authorization'] = 'Bearer ' + token
        if body is not None:
            headers['Content-Type'] = 'application/json'
        request = Request(self.base + path, data=json.dumps(body).encode() if body is not None else None, headers=headers, method=method)
        try:
            with urlopen(request, timeout=5) as response:
                raw = response.read()
                return response.status, json.loads(raw) if 'application/json' in response.headers['Content-Type'] else raw
        except HTTPError as error:
            return error.code, json.loads(error.read())


class BaselineHTTPTests(LabHarness):
    """Assert the deliberately vulnerable baseline behaves as the flaw requires."""

    TRAINING_VULNERABLE = True

    def test_session_and_authentication(self):
        status, session = self.request('GET', '/api/session')
        self.assertEqual(status, 200)
        self.assertEqual(session['build_stage'], 'baseline')
        self.assertEqual(session['mode'], 'training-vulnerable')
        self.assertIn('request_id', session)
        for token in (None, 'bad-pass', COLLECTOR_TOKEN):
            for path in ('/api/dossiers', '/api/dossiers/103', '/api/mission/status'):
                self.assertEqual(self.request('GET', path, token)[0], 401)

    def test_filtered_list_and_actual_seeded_permission_failure(self):
        status, response = self.request('GET', '/api/dossiers', ANALYST_TOKEN)
        self.assertEqual(status, 200)
        self.assertEqual([item['id'] for item in response['items']], [101, 102])
        for dossier_id in (101, 103, 104):
            status, response = self.request('GET', '/api/dossiers/%d' % dossier_id, ANALYST_TOKEN)
            self.assertEqual(status, 200)
            self.assertEqual(response['dossier']['id'], dossier_id)
        self.assertEqual(self.request('GET', '/api/dossiers/999', ANALYST_TOKEN)[0], 404)

    def test_operator_boundary_and_collector_purpose(self):
        for method, path in [('GET', '/api/collector/status'), ('POST', '/api/collector/revoke'),
                             ('POST', '/api/collector/simulate'), ('POST', '/api/mission/verify')]:
            self.assertEqual(self.request(method, path, ANALYST_TOKEN, {} if method == 'POST' else None)[0], 403)
            self.assertEqual(self.request(method, path, COLLECTOR_TOKEN, {} if method == 'POST' else None)[0], 401)
        for token in (None, 'bad-pass', ANALYST_TOKEN, OPERATOR_TOKEN):
            self.assertEqual(self.request('POST', '/api/collector/events', token, {})[0], 401)
        before = self.store.collector_status()['event_count']
        self.assertEqual(self.request('POST', '/api/collector/events', COLLECTOR_TOKEN, {'message_id': 'unknown'})[0], 400)
        self.assertEqual(self.request('POST', '/api/collector/events', COLLECTOR_TOKEN, {'text': 'Arbitrary real text is disallowed'})[0], 400)
        self.assertEqual(self.store.collector_status()['event_count'], before)
        status, result = self.request('POST', '/api/collector/events', COLLECTOR_TOKEN, {'message_id': 'message-raid-joke'})
        self.assertEqual(status, 201)
        self.assertTrue(result['accepted'])
        self.assertEqual(result['event_count'], before + 1)

    def test_actual_local_simulation_and_revocation_survive_restart(self):
        before = self.store.collector_status()['event_count']
        status, result = self.request('POST', '/api/collector/simulate', OPERATOR_TOKEN, {})
        self.assertEqual(status, 200)
        self.assertEqual(result['status'], 201)
        self.assertTrue(result['accepted'])
        self.assertEqual(result['event_count'], before + 1)
        self.assertIsNotNone(self.store.request_log(result['collector_response']['request_id']))
        self.assertEqual(self.request('POST', '/api/collector/revoke', OPERATOR_TOKEN, {})[0], 200)
        count = self.store.collector_status()['event_count']
        run_id = self.store.get('run_id')
        self.stop()
        self.store.close()
        self.store = Store(self.db, self.exports)
        self.start()
        self.assertEqual(self.store.get('run_id'), run_id)
        self.assertFalse(self.store.collector_status()['active'])
        self.assertEqual(self.request('POST', '/api/collector/events', COLLECTOR_TOKEN, {})[0], 403)
        self.assertEqual(self.store.collector_status()['event_count'], count)
        status, result = self.request('POST', '/api/collector/simulate', OPERATOR_TOKEN, {})
        self.assertFalse(result['accepted'])
        self.assertEqual(result['status'], 403)
        self.assertEqual(result['event_count'], count)

    def test_real_logged_evidence_export_survives_reset(self):
        status, result = self.request('GET', '/api/dossiers/103', ANALYST_TOKEN)
        request_id = result['request_id']
        status, result = self.request('POST', '/api/evidence', ANALYST_TOKEN, {'request_id': request_id, 'response': {'made_up': True}})
        self.assertEqual(status, 201)
        self.assertEqual(result['saved']['kind'], 'restricted-dossier')
        path = Path(self.temp.name) / result['saved']['path']
        exported = json.loads(path.read_text())
        self.assertEqual(exported['contents']['response']['body']['dossier']['id'], 103)
        self.assertNotIn('made_up', exported['contents']['response']['body'])
        self.assertEqual(exported['contents']['request_id'], request_id)
        self.assertEqual(self.request('POST', '/api/evidence', ANALYST_TOKEN, {'request_id': 'request-invented'})[0], 404)
        _, clue = self.request('POST', '/api/evidence', ANALYST_TOKEN, {'kind': 'clue'})
        self.assertEqual(clue['saved']['kind'], 'clue')
        old_run = self.store.get('run_id')
        self.store.revoke()
        self.store.reset()
        self.assertNotEqual(self.store.get('run_id'), old_run)
        self.assertTrue(self.store.collector_status()['active'])
        self.assertEqual(self.store.collector_status()['event_count'], 1)
        self.assertTrue(path.is_file())
        self.assertEqual(self.store.evidence(), [])

    def test_verification_performs_http_probes_and_does_not_claim_defence(self):
        self.request('POST', '/api/notes', ANALYST_TOKEN, {'observation': 'The same private joke appears on a slide.', 'hypothesis': 'A collection route may connect them.'})
        self.request('POST', '/api/evidence', ANALYST_TOKEN, {'kind': 'clue'})
        _, dossier = self.request('GET', '/api/dossiers/103', ANALYST_TOKEN)
        self.request('POST', '/api/evidence', ANALYST_TOKEN, {'request_id': dossier['request_id']})
        self.request('POST', '/api/collector/revoke', OPERATOR_TOKEN, {})
        count = self.store.collector_status()['event_count']
        status, verified = self.request('POST', '/api/mission/verify', OPERATOR_TOKEN, {})
        self.assertEqual(status, 200)
        checks = {item['key']: item for item in verified['checks']}
        self.assertFalse(checks['original']['passed'])
        self.assertEqual(checks['original']['status'], 200)
        self.assertFalse(checks['variant']['passed'])
        self.assertTrue(checks['authorised']['passed'])
        self.assertTrue(checks['filtered-list']['passed'])
        self.assertTrue(checks['collector']['passed'])
        self.assertFalse(verified['defence_attempted'])
        self.assertEqual(verified['outcome']['key'], 'incomplete')
        self.assertEqual(self.store.collector_status()['event_count'], count)
        for probe in verified['probes']:
            self.assertIsNotNone(self.store.request_log(probe['response']['request_id']))
        _, mission = self.request('GET', '/api/mission/status', ANALYST_TOKEN)
        self.assertIsNotNone(mission['verification'])
        self.request('POST', '/api/notes', ANALYST_TOKEN, {'observation': 'Changed note', 'hypothesis': 'Changed hypothesis'})
        _, mission = self.request('GET', '/api/mission/status', ANALYST_TOKEN)
        self.assertIsNone(mission['verification'])

    def test_optional_hint_assistance_is_recorded_and_reset(self):
        self.assertEqual(self.request('POST', '/api/mission/assistance', OPERATOR_TOKEN, {'kind': 'hint', 'level': 1})[0], 403)
        for body in ({'kind': 'hint', 'level': 0}, {'kind': 'hint', 'level': True}, {'kind': 'other', 'level': 1}):
            self.assertEqual(self.request('POST', '/api/mission/assistance', ANALYST_TOKEN, body)[0], 400)
        status, result = self.request('POST', '/api/mission/assistance', ANALYST_TOKEN, {'kind': 'hint', 'level': 2})
        self.assertEqual(status, 200)
        self.assertEqual(result['assistance'][0]['level'], 2)
        self.assertIn('at', result['assistance'][0])
        _, mission = self.request('GET', '/api/mission/status', ANALYST_TOKEN)
        self.assertEqual(mission['assistance'], result['assistance'])
        self.store.reset()
        _, mission = self.request('GET', '/api/mission/status', ANALYST_TOKEN)
        self.assertEqual(mission['assistance'], [])

    def test_static_traversal_and_cross_origin_blocked(self):
        for path in ('/../server.py', '/%2e%2e/server.py', '/web/../server.py', '/fixtures/story.json', '/var/watchtower.sqlite3', '/docs/STORY.md', '/evidence'):
            self.assertEqual(self.request('GET', path)[0], 404)
        self.assertEqual(self.request('GET', '/api/session', extra_headers={'Host': 'example.com'})[0], 400)
        self.assertEqual(self.request('POST', '/api/notes', ANALYST_TOKEN, {}, {'Origin': 'https://example.com'})[0], 403)

    def test_default_startup_serves_protected_build(self):
        import socket
        import time
        sock = socket.socket()
        sock.bind(('127.0.0.1', 0))
        port = sock.getsockname()[1]
        sock.close()
        proc = subprocess.Popen(
            [sys.executable, str(ROOT / 'server.py'), '--db', str(self.db), '--port', str(port)],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try:
            session = None
            for _ in range(40):
                try:
                    request = Request('http://127.0.0.1:%d/api/session' % port, headers={'Authorization': 'Bearer ' + ANALYST_TOKEN})
                    with urlopen(request, timeout=1) as response:
                        session = json.loads(response.read())
                    break
                except Exception:
                    time.sleep(0.1)
            self.assertIsNotNone(session, 'protected server did not start without the training flag')
            self.assertEqual(session['mode'], 'protected')
            self.assertEqual(session['build_stage'], 'defended')
        finally:
            proc.terminate()
            proc.wait(timeout=5)


class OutcomeClassificationTests(unittest.TestCase):
    """Isolated outcome scenarios are model checks, not live exercise claims."""

    def scenario(self, boundary=True, legitimate=True, collector=True):
        checks = [{'key': key, 'passed': passed} for key, passed in [('original', boundary), ('variant', boundary),
                  ('authorised', legitimate), ('filtered-list', legitimate), ('collector', collector), ('source-fresh', True)]]
        return {'checks': checks, 'collector_probe_at': '2026-10-10T14:30:00+00:00', 'defence_attempted': True}

    def test_all_endings_require_actual_evidence_and_completed_checks(self):
        notes = {'observation': 'A clue', 'hypothesis': 'A route'}
        evidence = [{'kind': 'clue'}, {'kind': 'restricted-dossier'}]
        self.assertEqual(derive_outcome(notes, evidence, None)['key'], 'incomplete')
        self.assertEqual(derive_outcome(notes, [], self.scenario())['key'], 'incomplete')
        self.assertEqual(derive_outcome(notes, evidence, self.scenario())['key'], 'victory')
        self.assertEqual(derive_outcome(notes, evidence, self.scenario(boundary=False, collector=False))['key'], 'raid-wipes')
        self.assertEqual(derive_outcome(notes, evidence, self.scenario(legitimate=False))['key'], 'raid-wipes')
        self.assertEqual(derive_outcome(notes, evidence, self.scenario(collector=False))['key'], 'incomplete')
        declaration = {'at': '2026-10-10T14:00:00+00:00'}
        self.assertEqual(derive_outcome(notes, evidence, self.scenario(collector=False), declaration)['key'], 'false-victory')
        self.assertEqual(derive_outcome(notes, evidence, self.scenario(boundary=False, collector=False), declaration)['key'], 'raid-wipes')
        self.assertEqual(derive_outcome(notes, evidence, self.scenario(collector=False), {'at': '2026-10-10T15:00:00+00:00'})['key'], 'incomplete')
        baseline = self.scenario(boundary=False)
        baseline['defence_attempted'] = False
        self.assertEqual(derive_outcome(notes, evidence, baseline)['key'], 'incomplete')


if __name__ == '__main__':
    unittest.main()


class ProtectedHTTPTests(LabHarness):
    """Replay the same requests against the repaired, protected build."""

    TRAINING_VULNERABLE = False

    def test_protected_boundary_blocks_cross_workspace(self):
        status, session = self.request('GET', '/api/session', ANALYST_TOKEN)
        self.assertEqual(status, 200)
        self.assertEqual(session['mode'], 'protected')
        # The analyst keeps its own demo workspace files.
        for dossier_id in (101, 102):
            status, response = self.request('GET', '/api/dossiers/%d' % dossier_id, ANALYST_TOKEN)
            self.assertEqual(status, 200)
            self.assertEqual(response['dossier']['id'], dossier_id)
        # Restricted files in other workspaces are now refused.
        for dossier_id in (103, 104, 105, 106):
            self.assertEqual(self.request('GET', '/api/dossiers/%d' % dossier_id, ANALYST_TOKEN)[0], 403)
        # The listing exposes only the analyst's own workspace.
        status, listing = self.request('GET', '/api/dossiers', ANALYST_TOKEN)
        self.assertEqual(status, 200)
        self.assertEqual({item['id'] for item in listing['items']}, {101, 102})

    def test_operator_still_reviews_every_workspace(self):
        for dossier_id in (101, 103, 104, 105, 106):
            self.assertEqual(self.request('GET', '/api/dossiers/%d' % dossier_id, OPERATOR_TOKEN)[0], 200)

    def test_missing_file_still_404_not_403(self):
        self.assertEqual(self.request('GET', '/api/dossiers/999', ANALYST_TOKEN)[0], 404)
