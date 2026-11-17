#!/usr/bin/env python3
"""Convert the processed router splits into MLX chat JSONL for 4-bit QLoRA-equivalent training."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from harnessproof.contracts import ROUTER_PREFIX


def read_jsonl(path):
    return [json.loads(line) for line in Path(path).read_text(encoding='utf8').splitlines() if line.strip()]


def request_from_prompt(prompt: str) -> str:
    if 'REQUEST:\n' not in prompt or '\nDECISION:' not in prompt:
        raise ValueError('Unexpected prompt format')
    return prompt.split('REQUEST:\n', 1)[1].rsplit('\nDECISION:', 1)[0]


def row(split_row):
    return {'messages': [
        {'role': 'system', 'content': ROUTER_PREFIX},
        {'role': 'user', 'content': request_from_prompt(split_row['prompt'])},
        {'role': 'assistant', 'content': split_row['completion']},
    ]}


def build(out_dir='data/mlx', source_dir='data/processed'):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    counts = {}
    for split in ('train', 'valid', 'test'):
        rows = read_jsonl(Path(source_dir) / f'{split}.jsonl')
        converted = [row(r) for r in rows]
        (out / f'{split}.jsonl').write_text(
            ''.join(json.dumps(r, ensure_ascii=False) + '\n' for r in converted), encoding='utf8')
        counts[split] = len(converted)
    (out / 'manifest.json').write_text(json.dumps({
        'format': 'mlx_chat_messages',
        'base_model_expected': 'mlx-community/Qwen2.5-0.5B-Instruct-4bit',
        'counts': counts,
        'note': '4-bit quantized base + LoRA is the MLX QLoRA-equivalent path; not bitsandbytes.',
    }, indent=2) + '\n')
    return counts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', default='data/mlx')
    ap.add_argument('--source', default='data/processed')
    args = ap.parse_args()
    print(json.dumps(build(args.out, args.source), indent=2))


if __name__ == '__main__':
    main()
