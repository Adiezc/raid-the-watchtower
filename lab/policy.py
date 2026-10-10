"""The active training permission boundary.

Baseline flaw (now repaired): the endpoint authenticated a caller but never
checked whether that caller was allowed to read the requested dossier, so any
signed-in account could open every restricted file. This is a broken
object-level authorisation failure (BOLA / IDOR).

The repair below decides access from the dossier's workspace and the account's
role, not merely from the presence of a valid token. The deliberate flaw is
still reachable, but only when the lab is started with the explicit
``--training-vulnerable`` flag, so the insecure version remains available for
the explicit educational replay while the protected build is the default.
"""

PROTECTED_IMPLEMENTED = True


def can_read_dossier(account, dossier, training_vulnerable=False):
    """Return whether ``account`` may read ``dossier``.

    Protected rule: a caller may read a dossier only when the dossier belongs to
    the caller's own workspace, or the caller holds the operator role (operators
    review every workspace). Authentication alone is not sufficient.

    When ``training_vulnerable`` is set, the original flaw is reproduced so the
    explicit training replay can demonstrate the insecure behaviour.
    """
    if account is None or dossier is None:
        return False
    if training_vulnerable:
        # Deliberately insecure baseline, kept for the educational replay only.
        return True
    if account.get('role') == 'operator':
        return True
    return dossier.get('workspace') == account.get('workspace')
