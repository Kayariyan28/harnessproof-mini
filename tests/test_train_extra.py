import json
from pathlib import Path

from harnessproof.cli import heuristic_route
from harnessproof.dataset import build_dataset, read_jsonl, signature
from harnessproof.quality import gate_from_directory

ROOT = Path(__file__).parents[1]


def test_train_extra_is_train_only_and_family_disjoint(tmp_path):
    extra = ROOT / 'data' / 'train_extra.jsonl'
    rows = list(read_jsonl(extra))
    assert len(rows) >= 150
    assert {row['split'] for row in rows} == {'train'}
    seed_families = {row['family'] for row in read_jsonl(ROOT / 'data' / 'seed_scenarios.jsonl')}
    assert not seed_families & {row['family'] for row in rows}
    prompts = [signature(row['prompt']) for row in rows]
    assert len(prompts) == len(set(prompts))


def test_build_with_extra_reaches_publish_scale_without_touching_holdout(tmp_path):
    baseline = build_dataset(ROOT / 'data' / 'seed_scenarios.jsonl', tmp_path / 'base')
    expanded = build_dataset(
        ROOT / 'data' / 'seed_scenarios.jsonl',
        tmp_path / 'expanded',
        train_extra_path=ROOT / 'data' / 'train_extra.jsonl',
    )
    assert baseline['valid'] == expanded['valid'] == 18
    assert baseline['test'] == expanded['test'] == 18
    assert expanded['train'] >= 200
    assert expanded['provenance']['opencode_session'] >= 150
    # Holdout prompts and labels must be byte-identical after expansion.
    for split in ('valid', 'test'):
        assert (tmp_path / 'base' / f'{split}.jsonl').read_text() == (tmp_path / 'expanded' / f'{split}.jsonl').read_text()
    # The heuristic baseline is unchanged by construction; its known failure stays visible.
    gold = list(read_jsonl(ROOT / 'data' / 'processed' / 'test.meta.jsonl'))
    wrong = [row['id'] for row in gold if heuristic_route(row['prompt'])['action'] != row['action']]
    assert wrong == ['ref-4-2']


def test_expanded_dataset_passes_publish_scale_gate(tmp_path):
    build_dataset(
        ROOT / 'data' / 'seed_scenarios.jsonl',
        tmp_path,
        train_extra_path=ROOT / 'data' / 'train_extra.jsonl',
    )
    report = gate_from_directory(tmp_path, mode='publish')
    assert report['passed'], report['failures']
    assert report['action_counts'].keys() == {'retrieve', 'calculate', 'clock', 'answer', 'clarify', 'refuse'}
    assert report['families'] >= 18
