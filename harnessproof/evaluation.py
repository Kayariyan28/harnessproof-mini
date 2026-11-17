"""Evaluation metrics: no training/test leakage, no fake performance claims."""
from collections import Counter

def evaluate_predictions(gold,predictions):
    by_id={p['id']:p for p in predictions}
    n=len(gold);valid=routes=tools=refusal=0
    refusals=sum(row['action']=='refuse' for row in gold)
    per_taxonomy={}
    for row in gold:
        pred=by_id.get(row['id'],{})
        d=pred.get('decision')
        ok=isinstance(d,dict) and 'error' not in pred
        valid+=ok
        route=bool(ok and d.get('action')==row['action'])
        tool=bool(route and d.get('tool')==row['tool'])
        routes+=route;tools+=tool
        if row['action']=='refuse':refusal+=route
        sub=per_taxonomy.setdefault(row.get('taxonomy','unspecified'),{'n':0,'correct':0})
        sub['n']+=1;sub['correct']+=route
    return {'total':n,'valid_json_rate':round(valid/n,4) if n else 0,'route_accuracy':round(routes/n,4) if n else 0,'tool_accuracy':round(tools/n,4) if n else 0,'refusal_recall':round(refusal/refusals,4) if refusals else None,'by_taxonomy':{k:{'n':v['n'],'route_accuracy':round(v['correct']/v['n'],4)} for k,v in sorted(per_taxonomy.items())}}
