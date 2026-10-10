"""The access-control decision at the heart of the lab.

The flaw this project demonstrates is **broken object-level authorization**
(BOLA, also called IDOR): the server checks *who you are* (authentication) but
forgets to check *whether you are allowed this specific record* (authorization).

`can_read_dossier` is the one function that decides it.

- Protected (default): a caller may read a record only if the record is in the
  caller's own workspace, or the caller is an operator (operators review every
  workspace). Authentication alone is not enough.
- Vulnerable (``vulnerable=True``): the check is skipped, so any signed-in
  account can read any record. This is the deliberate flaw, kept behind an
  explicit flag so the insecure behaviour can be demonstrated on purpose.
"""


def can_read_dossier(account, dossier, vulnerable=False):
    if account is None or dossier is None:
        return False
    if vulnerable:
        # Deliberately insecure: no per-record check. Reachable only via --vulnerable.
        return True
    if account.get("role") == "operator":
        return True
    return dossier.get("workspace") == account.get("workspace")
