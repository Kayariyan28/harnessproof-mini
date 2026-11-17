#!/usr/bin/env python3
"""Lightweight prepublication audit; manual scrutiny is still required."""
import json
import re
from pathlib import Path

PATTERNS = {
    'private_key': re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'),
    'possible_live_secret': re.compile(r'(?:sk-|ghp_|hf_)[A-Za-z0-9_-]{24,}'),
}
EXTS = {'.py', '.md', '.json', '.jsonl', '.yaml', '.yml', '.txt', '.toml', '.ipynb', '.example'}

def audit(root=Path('.')):
    violations = []
    count = 0
    for path in sorted(Path(root).rglob('*')):
        if not path.is_file() or path.suffix not in EXTS:
            continue
        if any(part.startswith('.') and part not in ('.opencode', '.github', '.devcontainer') for part in path.parts):
            continue
        if any(part in ('runs', '__pycache__', '.venv') for part in path.parts):
            continue
        if path.stat().st_size > 2_000_000:
            continue
        count += 1
        content = path.read_text(encoding='utf8', errors='replace')
        for label, regex in PATTERNS.items():
            if regex.search(content):
                violations.append({'file': str(path), 'type': label})
    return {
        'scanned_files': count, 'passed': not violations,
        'possible_secrets': violations,
        'limitation': 'Heuristic scanning is not a guarantee. Inspect git history and notebook outputs manually.'
    }

if __name__ == '__main__':
    result = audit()
    print(json.dumps(result, indent=2))
    if not result['passed']:
        raise SystemExit(2)
