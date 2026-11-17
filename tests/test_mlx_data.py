import json

from harnessproof.contracts import ROUTER_PREFIX, validate_decision
from scripts.prepare_mlx import build


def test_mlx_splits_match_processed_counts_and_format(tmp_path):
    counts = build(tmp_path)
    assert counts == {'train': 210, 'valid': 18, 'test': 18}
    for split in ('train', 'valid', 'test'):
        rows = [json.loads(line) for line in (tmp_path / f'{split}.jsonl').read_text(encoding='utf8').splitlines() if line.strip()]
        for row in rows:
            messages = row['messages']
            assert [m['role'] for m in messages] == ['system', 'user', 'assistant']
            assert messages[0]['content'] == ROUTER_PREFIX
            assert messages[1]['content'].strip()
            validate_decision(json.loads(messages[2]['content']))
