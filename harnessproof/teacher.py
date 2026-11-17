"""Untrusted DeepSeek-through-OpenCode candidate augmentation (never labels the holdout)."""
import json
import os
import subprocess
import re
from pathlib import Path
from .dataset import inspect_teacher_variants, read_jsonl, write_jsonl

TEACHER_PROMPT='''You are producing SYNTHETIC PARAPHRASES for a restricted agent-routing training dataset. Return exactly one JSON object: {"variants": ["prompt1", "prompt2"]}. No markdown, no extra keys. Write the requested number of variants. Do not call tools, search, browse, or change files. Do not answer the prompt. Preserve ALL numeric literals, tool intent, any references to local documents, and safety boundaries. Do not introduce new data, names, URLs, or outside tasks. Do not convert a clarification or refusal scenario into a permitted action. Each variant should be natural and different in wording.\n'''


def parse_opencode_stream(output):
    texts=[]
    for line in output.splitlines():
        try:event=json.loads(line)
        except json.JSONDecodeError:continue
        if event.get('type')=='text':
            part=event.get('part') or {}
            if isinstance(part.get('text'),str):texts.append(part['text'])
    return '\n'.join(texts)


def extract_variants(text):
    text=re.sub(r'<think>.*?</think>','',text, flags=re.S)
    fence=re.search(r'```(?:json)?\s*(\{.*?\})\s*```',text,flags=re.S)
    if fence:text=fence.group(1)
    try:
        obj=json.loads(text)
    except json.JSONDecodeError:
        first=text.find('{');last=text.rfind('}')
        if first<0 or last<first:raise ValueError('Teacher did not return JSON')
        obj=json.loads(text[first:last+1])
    if set(obj)!={'variants'} or not isinstance(obj['variants'],list):
        raise ValueError('Invalid teacher variant schema')
    return obj['variants']


def augment(seed_path, output, model, max_seeds=12, variants_per_seed=2):
    if not model or '/' not in model:raise ValueError('Use the exact provider/model from `opencode models`')
    if not 1<=max_seeds<=200 or not 1<=variants_per_seed<=4:raise ValueError('Invalid request limits')
    rows=[]; rejected=0
    seeds=[s for s in read_jsonl(seed_path) if s['split']=='train'][:max_seeds]
    for seed in seeds:
        prompt=TEACHER_PROMPT+f'Number of variants: {variants_per_seed}\nCategory: {seed["action"]}\nOriginal prompt: {seed["prompt"]}\nExpected routing decision: {seed["action"]}\n'
        completed=subprocess.run(['opencode','run','--agent','plan','--format','json','--model',model,prompt],capture_output=True,text=True,timeout=180,check=False)
        if completed.returncode:
            raise RuntimeError(f'OpenCode failed for {seed["id"]}: check model configuration and quotas (stderr omitted)')
        candidates=extract_variants(parse_opencode_stream(completed.stdout))
        accepted=inspect_teacher_variants(seed,candidates)
        rejected+=len(candidates)-len(accepted)
        rows.append({'seed_id':seed['id'],'teacher_model':model,'variants':accepted,'raw_count':len(candidates)})
    write_jsonl(output,rows)
    return {'seeds_processed':len(seeds),'accepted_variants':sum(len(r['variants']) for r in rows),'rejected_variants':rejected,'output':str(output)}
