"""Derive fictional endings from recorded observations and HTTP checks."""


def derive_outcome(notes, evidence, verification, declaration=None):
    remaining = []
    if not notes.get('observation', '').strip():
        remaining.append('Record what you observed in the guild message and sales slide.')
    if not notes.get('hypothesis', '').strip():
        remaining.append('Record your initial explanation, including any uncertainty.')
    kinds = {item.get('kind') for item in evidence}
    if 'clue' not in kinds:
        remaining.append('Preserve the guild message and matching sales slide.')
    if 'restricted-dossier' not in kinds:
        remaining.append('Preserve one real restricted dossier response from your investigation.')
    if not verification:
        remaining.append('Complete the defensive verification with the operator.')
    elif verification.get('defence_attempted') is False:
        remaining.append('Review and apply the permission repair, then repeat verification in protected mode.')
    if remaining:
        return {'key': 'incomplete', 'title': 'Investigation in progress',
                'explanation': 'The lab has not yet established a completed protective result.',
                'remaining': remaining}
    checks = {item['key']: item for item in verification['checks']}
    boundary_ok = all(checks.get(key, {}).get('passed') for key in ('original', 'variant'))
    legitimate_ok = all(checks.get(key, {}).get('passed') for key in ('authorised', 'filtered-list'))
    source_ok = checks.get('source-fresh', {}).get('passed', True)
    if not boundary_ok or not legitimate_ok or not source_ok:
        return {'key': 'raid-wipes', 'title': 'The Raid Wipes',
                'explanation': 'Completed checks did not establish a working permission boundary with legitimate access intact. Review the failed checks before trying again.',
                'remaining': []}
    if not checks.get('collector', {}).get('passed'):
        collector_time = verification.get('collector_probe_at', '')
        claim_time = declaration.get('at', '') if declaration else ''
        if claim_time and claim_time < collector_time:
            return {'key': 'false-victory', 'title': 'The False Victory',
                    'explanation': 'Victory was explicitly declared before the collection retest. The repaired dossier boundary works, but a new synthetic guild event was still accepted.',
                    'remaining': []}
        return {'key': 'incomplete', 'title': 'Containment still needed',
                'explanation': 'Dossier access is repaired, but the mock collector still accepts events.',
                'remaining': ['Revoke the mock collector credential and repeat verification.']}
    return {'key': 'victory', 'title': 'Victory With Loose Ends',
            'explanation': 'Evidence is preserved, both restricted requests are blocked, legitimate access works and new collection is rejected. In the fictional epilogue one buyer pauses its purchase. Existing records remain and the wider struggle continues.',
            'remaining': []}
