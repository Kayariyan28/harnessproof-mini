"""Zero-dependency dataset release gate; do not confuse heuristic checks with human review."""
from collections import Counter
from pathlib import Path
import json
from .dataset import read_jsonl, signature


def quality_report(rows, metadata, mode='pilot'):
    if mode not in ('pilot','publish'):
        raise ValueError('mode must be pilot or publish')
    failures=[]
    minimum={'pilot':1,'publish':200}[mode]
    if len(rows.get('train',[]))<minimum:
        failures.append(f'training_size:{len(rows.get("train",[]))}<{minimum}')
    if any(not rows.get(s) for s in ('valid','test')):
        failures.append('empty_holdout')
    families={}; normalized={}; counts=Counter();taxonomies=Counter();provenance=Counter()
    for split in ('train','valid','test'):
        records=metadata.get(split,[])
        if len(records)!=len(rows.get(split,[])):
            failures.append(f'metadata_alignment:{split}')
        for row in records:
            family=row.get('family')
            if family in families and families[family]!=split:
                failures.append('family_leakage')
            families[family]=split
            sig=signature(row.get('prompt',''))
            if sig in normalized and normalized[sig]!=split:
                failures.append('exact_prompt_leakage')
            normalized[sig]=split
            counts[row.get('action','unknown')]+=1
            taxonomies[row.get('taxonomy','unknown')]+=1
            provenance[row.get('provenance','unknown')]+=1
    if mode=='publish':
        if len(families)<18:failures.append('family_diversity:need_18')
        if len(counts)<6:failures.append('action_diversity:need_6')
        if any(v<10 for v in counts.values()):failures.append('class_balance:each_action_10')
    return {'passed':not failures,'mode':mode,'counts':{s:len(rows.get(s,[])) for s in ('train','valid','test')},
            'families':len(families),'action_counts':dict(counts),'taxonomy_counts':dict(taxonomies),
            'provenance_counts':dict(provenance),'failures':sorted(set(failures)),
            'limitations':['Heuristics do not establish semantic correctness','Human review and generated-data provenance are required before release']}


def gate_from_directory(directory='data/processed',mode='pilot'):
    p=Path(directory)
    rows={s:list(read_jsonl(p/f'{s}.jsonl')) for s in ('train','valid','test')}
    metadata={s:list(read_jsonl(p/f'{s}.meta.jsonl')) for s in ('train','valid','test')}
    return quality_report(rows,metadata,mode)
