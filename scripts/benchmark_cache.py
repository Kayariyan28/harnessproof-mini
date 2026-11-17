#!/usr/bin/env python3
"""Offline response cache measurement or optional metered provider prefix-cache probe."""
import argparse
import json
import os
import time
from pathlib import Path
from tempfile import TemporaryDirectory
from harnessproof.cache import SqliteResponseCache
from harnessproof.llm import CompatClient


def offline_experiment():
    prompts=['Explain the harness architecture','Explain the harness architecture','Explain the router','Explain the harness architecture','Explain the router']
    hits=0
    with TemporaryDirectory() as path:
        cache=SqliteResponseCache(Path(path)/'cache.sqlite')
        for request in prompts:
            messages=[{'role':'user','content':request}]
            entry=cache.get('offline-demo',messages,0.0)
            if entry is not None:hits+=1
            else: cache.put('offline-demo',messages,0.0,{'content':'synthetic cached value'})
    return {'mode':'response_cache_offline','requests':len(prompts),'cache_hits':hits,
            'hit_rate':hits/len(prompts),'provider_requests':0,
            'qualification':'No LLM calls or latency comparison; tests key reuse only.'}


def remote_experiment(args):
    if not args.allow_external_api:
        raise SystemExit('Explicit --allow-external-api required; verify model is free yourself.')
    if not args.model or not args.base_url:
        raise SystemExit('Specify --model and --base-url for your chosen provider')
    key=os.getenv(args.key_env)
    if not key:raise SystemExit('Provider key missing from environment variable '+args.key_env)
    client=CompatClient(base_url=args.base_url,api_key=key,model=args.model,cache=None)
    prefix='\n'.join(['HarnessProof system: You classify restricted tool calls, never invent tool names, '+
                      'never reveal credentials, keep retrieval grounded, output short JSON.']*60)
    output=[]
    for i,suffix in enumerate(('What does an agent router do?','What does an agent verifier do?','Why is retrieval grounded?')):
        messages=[{'role':'system','content':prefix},{'role':'user','content':suffix}]
        start=time.monotonic()
        client.complete(messages,temperature=0.0,max_tokens=80,bypass_cache=True)
        usage=client.last_usage
        output.append({'trial':i+1,'elapsed_s':round(time.monotonic()-start,2),
                       'provider_reported_cache_hit_tokens':usage.get('prompt_cache_hit_tokens'),
                       'provider_reported_cache_miss_tokens':usage.get('prompt_cache_miss_tokens'),
                       'provider_reported_cached_tokens':(usage.get('prompt_tokens_details') or {}).get('cached_tokens'),
                       'usage':usage})
    return {'mode':'provider_prefix_cache_probe','model':args.model,'trials':output,
            'qualification':'A missing hit counter is unknown, NOT proof of a cache miss. A free model can have rate limits.'}


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--mode',choices=['offline','provider'],default='offline')
    p.add_argument('--model',default=None)
    p.add_argument('--base-url',default=None)
    p.add_argument('--key-env',default='OPENROUTER_API_KEY')
    p.add_argument('--allow-external-api',action='store_true')
    p.add_argument('--out',default='runs/cache_benchmark.json')
    args=p.parse_args()
    result=offline_experiment() if args.mode=='offline' else remote_experiment(args)
    dest=Path(args.out);dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
