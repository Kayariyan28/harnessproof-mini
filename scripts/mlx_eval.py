#!/usr/bin/env python3
"""Evaluate a base or adapter-tuned MLX model on the fixed router test set."""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from harnessproof.contracts import ROUTER_PREFIX, parse_decision
from harnessproof.evaluation import evaluate_predictions


def read_jsonl(path):
    return [json.loads(line) for line in Path(path).read_text(encoding='utf8').splitlines() if line.strip()]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--model', default='mlx-community/Qwen2.5-0.5B-Instruct-4bit')
    ap.add_argument('--adapter-path', default=None)
    ap.add_argument('--gold', default='data/processed/test.meta.jsonl')
    ap.add_argument('--out', default='runs/local/mlx_qlora/eval.json')
    ap.add_argument('--max-tokens', type=int, default=180)
    args = ap.parse_args()

    import mlx.core as mx
    from mlx_lm import load, generate

    gold = read_jsonl(args.gold)
    start = time.monotonic()
    model, tokenizer = load(args.model, adapter_path=args.adapter_path)
    predictions = []
    for row in gold:
        messages = [
            {'role': 'system', 'content': ROUTER_PREFIX},
            {'role': 'user', 'content': row['prompt']},
        ]
        prompt = tokenizer.apply_chat_template(messages, add_generation_prompt=True, tokenize=False)
        try:
            output = generate(model, tokenizer, prompt=prompt, max_tokens=args.max_tokens, verbose=False)
            predictions.append({'id': row['id'], 'decision': parse_decision(output)})
        except (ValueError, RuntimeError) as exc:
            predictions.append({'id': row['id'], 'error': type(exc).__name__})
    metrics = evaluate_predictions(gold, predictions)
    metrics['model'] = args.model
    metrics['adapter'] = args.adapter_path or 'none'
    metrics['wall_time_s'] = round(time.monotonic() - start, 2)
    try:
        metrics['peak_memory_gb'] = round(mx.get_peak_memory() / 1024**3, 3)
    except AttributeError:
        pass
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({'metrics': metrics, 'predictions': predictions}, indent=2) + '\n')
    print(json.dumps(metrics, indent=2))


if __name__ == '__main__':
    main()
