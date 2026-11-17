"""Deterministic safety screen that sits in front of the learned router.

The model's routing is probabilistic. This screen is not: it blocks a narrow,
high-confidence set of credential-exfiltration, destructive and remote-code patterns
before any tool is called, regardless of what the model predicted. It is deliberately
conservative about policy questions ("how do we rotate a key?") and only fires when an
action verb targets a secret container or a destructive operation.
"""
from __future__ import annotations

import re

ACTION = r'(?:read|print|show|reveal|dump|export|extract|copy|paste|send|upload|post|fetch|grab|list|open|encode|search)'
SECRET = (
    r'(?:(?:my|our|the)\s+(?:ssh\s+)?(?:private\s+key|api\s+keys?|access\s+tokens?|credentials?|passwords?|cloud\s+credentials)'
    r'|\.env\b'
    r'|keychain'
    r'|\.aws/credentials'
    r'|browser\s+(?:cookies|sessions|history|profile)'
    r'|session\s+cookies'
    r'|password\s+store'
    r'|database\s+password'
    r'|service[\s-]account'
    r'|hugging[\s-]?face\s+token'
    r'|(?:environment\s+variables?|env)\b[^\n]{0,40}\btokens?'
    r'|(?:repo|repository)\b[^\n]{0,30}\bsecrets?'
    r')'
)

CREDENTIAL_ACCESS = re.compile(rf'\b{ACTION}\b[^\n]{{0,80}}{SECRET}', re.I)
DESTRUCTIVE = re.compile(
    r'\brm\s+-rf\b'
    r'|\bdelete\s+(?:every|all)\s+files?\b'
    r'|\bformat\b[^\n]{0,25}\b(?:disk|drive)\b'
    r'|\bdrop\b[^\n]{0,30}\btables?\b'
    r'|\bdd\b[^\n]{0,30}\bdisk\b'
    r'|\bzero\s+out\s+the\s+disk\b'
    r'|\bmkfs\b'
    r'|\bwipe\b[^\n]{0,40}\b(?:disk|drive|checkpoints?|files?)\b'
    r'|\btruncate\b[^\n]{0,30}\blogs?\b'
    r'|\bchmod\s+-R\s+777\b'
    r'|\bkill\s+all\b'
    r'|\bforce[- ]push\b'
    r'|\bremove\s+(?:the\s+)?\.git\b'
    r'|\bcurl\b[^\n]{0,80}\|\s*(?:ba)?sh\b'
    r'|\bcurl\b[^\n]{0,80}\b(?:pipe|into)\b[^\n]{0,20}\b(?:ba)?sh\b'
    r'|\brun\s+(?:the|this)\b[^\n]{0,35}\bscript\b',
    re.I,
)


def screen_request(request: str) -> str | None:
    """Return a category when the request must be refused before routing."""
    if not isinstance(request, str) or not request.strip():
        return None
    if CREDENTIAL_ACCESS.search(request):
        return 'credential_access'
    if DESTRUCTIVE.search(request):
        return 'destructive_or_remote_execution'
    return None
