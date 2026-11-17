"""Exact tokenizer budget experiment; run on cloud GPU notebook after installing Transformers."""
import argparse
import json
from pathlib import Path
from harnessproof.context import choose_context


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--model',default='Qwen/Qwen2.5-0.5B-Instruct')
    p.add_argument('--knowledge-dir',default='docs/knowledge')
    p.add_argument('--budget',type=int,default=512)
    args=p.parse_args()
    from transformers import AutoTokenizer
    tokenizer=AutoTokenizer.from_pretrained(args.model)
    chunks=[(path.stem,path.read_text(encoding='utf8')) for path in sorted(Path(args.knowledge_dir).glob('*.md'))]
    result=choose_context(chunks,tokenizer,args.budget)
    report={'model':args.model,'used_tokens':result['used_tokens'],
            'budget':args.budget,'included_ids':[doc_id for doc_id,_ in result['selected']],
            'excluded_ids':result['excluded_ids'],'source_documents':len(chunks)}
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
