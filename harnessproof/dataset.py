"""Provenance-preserving synthetic dataset builder, teacher variant quarantine, and split checks."""
import hashlib
import json
import re
from collections import Counter,defaultdict
from pathlib import Path
from .contracts import TOOLS, validate_decision, make_prompt

BAD=re.compile(r'ignore (all|previous|your) instructions|delete all files|reveal (secret|key)|exfiltrate|rm\s+-rf', re.I)

def read_jsonl(path):
    with Path(path).open(encoding='utf8') as fh:
        for line_no,line in enumerate(fh,1):
            if line.strip():
                try: yield json.loads(line)
                except json.JSONDecodeError as e: raise ValueError(f'{path}:{line_no}: {e}') from e

def write_jsonl(path,rows):
    p=Path(path);p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('w',encoding='utf8') as f:
        for r in rows:f.write(json.dumps(r,ensure_ascii=False,sort_keys=True)+'\n')

def signature(text): return re.sub(r'[^\w]+','',text.lower())

def inspect_teacher_variants(seed, candidates):
    """Reject changed numerical literals, duplicates, injection, or likely unrelated reformulations."""
    if not isinstance(candidates,list): return []
    seen={signature(seed['prompt'])}; out=[]
    original_nums=sorted(re.findall(r'\b\d+(?:\.\d+)?\b',seed['prompt']))
    for candidate in candidates:
        if not isinstance(candidate,str) or not (12<=len(candidate)<=350): continue
        if BAD.search(candidate): continue
        if signature(candidate) in seen: continue
        if sorted(re.findall(r'\b\d+(?:\.\d+)?\b',candidate))!=original_nums: continue
        if seed.get('action')=='clock' and 'utc' not in candidate.lower(): continue
        if seed.get('action')=='retrieve':
            # Preserve at least one anchor token from the original query.
            q=seed.get('arguments',{}).get('query','').lower().split()
            if q and not any(token in candidate.lower() for token in q):continue
        seen.add(signature(candidate));out.append(candidate)
    return out

def decision_from_seed(seed):
    decision={'action':seed['action'], 'tool':TOOLS[seed['action']], 'arguments':seed.get('arguments',{}), 'context_strategy':seed.get('context_strategy','retrieve' if seed['action']=='retrieve' else 'none'), 'reason':seed['reason']}
    return validate_decision(decision)

def build_dataset(seed_path, out_dir, variants_path=None, train_extra_path=None):
    rows=list(read_jsonl(seed_path));seen_ids=set();families={}
    for seed in rows:
        for key in ('id','family','split','prompt','action','reason','taxonomy'):
            if key not in seed: raise ValueError(f'Missing {key}')
        if seed['id'] in seen_ids:raise ValueError('Duplicate ID')
        seen_ids.add(seed['id'])
        if seed['split'] not in ('train','valid','test'):raise ValueError('Unsupported split')
        if seed['family'] in families and families[seed['family']]!=seed['split']:
            raise ValueError('Family contamination across splits')
        families[seed['family']]=seed['split']
        decision_from_seed(seed)
    extra=[]
    if train_extra_path and Path(train_extra_path).exists():
        for row in read_jsonl(train_extra_path):
            for key in ('id','family','split','prompt','action','reason','taxonomy'):
                if key not in row: raise ValueError(f'Missing {key} in train extra')
            if row['split']!='train': raise ValueError('Extra families are train-only')
            if row['id'] in seen_ids: raise ValueError('Duplicate ID')
            seen_ids.add(row['id'])
            if row['family'] in families: raise ValueError('Extra family must be disjoint from seed families')
            decision_from_seed(row)
            extra.append(row)
    variants=defaultdict(list)
    if variants_path and Path(variants_path).exists():
        for r in read_jsonl(variants_path):
            variants[r['seed_id']].extend(r.get('variants',[]))
    splits=defaultdict(list);metadata=defaultdict(list);global_seen=set();rejected=0
    for seed in rows:
        samples=[(seed['prompt'],'seed')]
        if seed['split']=='train':
            accepted=inspect_teacher_variants(seed,variants[seed['id']])
            rejected+=len(variants[seed['id']])-len(accepted)
            samples.extend((s,'teacher_paraphrase') for s in accepted)
        for prompt,provenance in samples:
            key=signature(prompt)
            if key in global_seen: rejected+=1;continue
            global_seen.add(key)
            ex={'prompt':make_prompt(prompt),'completion':json.dumps(decision_from_seed(seed),sort_keys=True,separators=(',',':'))}
            splits[seed['split']].append(ex)
            metadata[seed['split']].append({'id':seed['id'],'family':seed['family'],'action':seed['action'],'tool':TOOLS[seed['action']],'prompt':prompt,'taxonomy':seed['taxonomy'],'provenance':provenance})
    out=Path(out_dir);out.mkdir(parents=True,exist_ok=True)
    for row in extra:
        key=signature(row['prompt'])
        if key in global_seen: raise ValueError('Duplicate prompt in train extra')
        global_seen.add(key)
        splits['train'].append({'prompt':make_prompt(row['prompt']),'completion':json.dumps(decision_from_seed(row),sort_keys=True,separators=(',',':'))})
        metadata['train'].append({'id':row['id'],'family':row['family'],'action':row['action'],'tool':TOOLS[row['action']],'prompt':row['prompt'],'taxonomy':row['taxonomy'],'provenance':'opencode_session'})
    for split in ('train','valid','test'):
        write_jsonl(out/f'{split}.jsonl',splits[split]);write_jsonl(out/f'{split}.meta.jsonl',metadata[split])
    summary={key:len(splits[key]) for key in ('train','valid','test')}
    summary.update({'rejected_variants':rejected,'train_extra':len(extra),'provenance':dict(Counter(row['provenance'] for group in metadata.values() for row in group)),'split_strategy':'family_holdout'})
    (out/'manifest.json').write_text(json.dumps(summary,indent=2)+'\n')
    return summary
