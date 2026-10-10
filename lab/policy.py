"""The active training permission boundary.

This baseline deliberately authenticates a caller but does not check whether
the caller owns the requested dossier. The later blue defence edits this file.
"""

PROTECTED_IMPLEMENTED = False


def can_read_dossier(account, dossier, training_vulnerable=False):
    """Baseline flaw: any authenticated lab account can read any dossier."""
    return account is not None
