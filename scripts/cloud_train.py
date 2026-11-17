#!/usr/bin/env python3
"""Cloud GPU SFT: zero local GPU dependency; tiny Qwen baseline/LoRA/QLoRA/full comparison.

This script requires NVIDIA CUDA on Colab/Kaggle. CPU/cloud-Codespaces training is explicitly disallowed.
Never uploads or publishes weights, datasets or traces automatically.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import platform
import time
from pathlib import Path


def parse_args(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument('--mode', choices=['lora', 'qlora', 'full'], default='qlora')
    ap.add_argument('--model', default='Qwen/Qwen2.5-0.5B-Instruct')
    ap.add_argument('--data-dir', default='data/processed')
    ap.add_argument('--output-dir', default=None)
    ap.add_argument('--steps', type=int, default=40)
    ap.add_argument('--batch-size', type=int, default=1)
    ap.add_argument('--gradient-accumulation', type=int, default=8)
    ap.add_argument('--max-length', type=int, default=512)
    ap.add_argument('--eval-max', type=int, default=18)
    ap.add_argument('--rank', type=int, default=8)
    ap.add_argument('--seed', type=int, default=42)
    ap.add_argument('--device', choices=['auto', 'cuda', 'mps', 'cpu'], default='auto',
                    help='auto prefers CUDA, then Apple MPS, then CPU. QLoRA requires CUDA.')
    ap.add_argument('--skip-training', action='store_true', help='Evaluate pretrained baseline only.')
    args=ap.parse_args(argv)
    if args.steps < 1 or args.steps > 1000:
        ap.error('Use 1-1000 steps to bound free GPU consumption')
    if args.eval_max < 1 or args.eval_max > 200:
        ap.error('Use 1-200 evaluation examples')
    if args.max_length < 64 or args.max_length > 4096:
        ap.error('Use a bounded context length')
    if args.rank < 1 or args.rank > 128: ap.error('Invalid LoRA rank')
    return args


def load_records(folder, split):
    file=Path(folder)/f'{split}.jsonl'
    if not file.exists():raise FileNotFoundError(f'Build data first: {file}')
    rows=[json.loads(line) for line in file.read_text(encoding='utf8').splitlines() if line.strip()]
    if not rows or any(set(x)!= {'prompt','completion'} for x in rows):
        raise ValueError(f'Invalid {split}.jsonl schema or empty split')
    return rows


def file_hash(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def judge_predictions(model, tokenizer, gold, device, max_items=18):
    import torch
    from harnessproof.contracts import parse_decision
    from harnessproof.evaluation import evaluate_predictions
    # Gold metadata has human-authored route labels; never use model-generated labels for holdout.
    predictions=[]
    model.eval()
    for i, row in enumerate(gold[:max_items]):
        from harnessproof.contracts import make_prompt
        encoded=tokenizer(make_prompt(row['prompt']),return_tensors='pt',truncation=True,max_length=1024)
        encoded={k:v.to(device) for k,v in encoded.items()}
        try:
            with torch.inference_mode():
                seq=model.generate(**encoded,max_new_tokens=160,do_sample=False,pad_token_id=tokenizer.eos_token_id)
            output=tokenizer.decode(seq[0,encoded['input_ids'].shape[1]:],skip_special_tokens=True)
            prediction=parse_decision(output)
            predictions.append({'id':row['id'],'decision':prediction})
        except (ValueError, RuntimeError, TypeError, KeyError) as ex:
            predictions.append({'id':row['id'],'error':type(ex).__name__})
    metrics=evaluate_predictions(gold[:max_items],predictions)
    return {'metrics':metrics, 'predictions':predictions}


def main(argv=None):
    args=parse_args(argv)
    try:
        import torch
        from datasets import Dataset
        from peft import LoraConfig
        from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig, set_seed
        from trl import SFTConfig, SFTTrainer
    except ImportError as exc:
        raise SystemExit('Missing cloud training requirements. Run: pip install -r requirements-cloud.txt') from exc
    if not torch.cuda.is_available() and args.device == 'cuda':
        raise SystemExit('CUDA requested but unavailable.')
    if args.device == 'cuda' and not torch.cuda.is_available():
        raise SystemExit('A CUDA GPU is required for --device cuda.')
    if args.device == 'auto':
        device = 'cuda' if torch.cuda.is_available() else ('mps' if torch.backends.mps.is_available() else 'cpu')
    else:
        device = args.device
    if device == 'cuda' and not torch.cuda.is_available():
        raise SystemExit('A CUDA GPU is required. Enable free T4/P100 or use --device mps on Apple Silicon.')
    if device == 'mps' and not torch.backends.mps.is_available():
        raise SystemExit('MPS requested but Apple Metal is unavailable.')
    if args.mode == 'qlora' and device != 'cuda':
        raise SystemExit('QLoRA 4-bit needs CUDA/bitsandbytes. Use --device mps --mode lora locally.')
    if device == 'cuda':
        dtype = torch.bfloat16 if torch.cuda.is_bf16_supported() else torch.float16
    elif device == 'mps':
        dtype = torch.float32  # MPS mixed precision is provider-dependent; fp32 is the stable path.
    else:
        dtype = torch.float32
    set_seed(args.seed)
    work=Path(args.output_dir or f'runs/cloud/{args.mode}')
    work.mkdir(parents=True,exist_ok=True)
    train=load_records(args.data_dir,'train')
    valid=load_records(args.data_dir,'valid')
    gold_file=Path(args.data_dir)/'test.meta.jsonl'
    gold=[json.loads(l) for l in gold_file.read_text(encoding='utf8').splitlines() if l.strip()]
    if not gold: raise ValueError('The test set must not be empty')
    tokenizer=AutoTokenizer.from_pretrained(args.model)
    if tokenizer.pad_token is None:tokenizer.pad_token=tokenizer.eos_token
    kwargs={'dtype':dtype}
    if device=='cuda':
        kwargs['low_cpu_mem_usage']=True
    if args.mode=='qlora':
        kwargs['quantization_config']=BitsAndBytesConfig(load_in_4bit=True,bnb_4bit_quant_type='nf4',bnb_4bit_use_double_quant=True,bnb_4bit_compute_dtype=dtype)
        kwargs['device_map']={'':0}
    start=time.monotonic()
    model=AutoModelForCausalLM.from_pretrained(args.model,**kwargs)
    if args.mode!='qlora': model=model.to(device)
    baseline=judge_predictions(model,tokenizer,gold,device,max_items=args.eval_max)
    (work/'baseline.json').write_text(json.dumps(baseline,indent=2,ensure_ascii=False)+'\n')
    metrics={'mode':args.mode,'base_model':args.model,'seed':args.seed,'steps_requested':args.steps,
             'train_examples':len(train),'valid_examples':len(valid),'test_examples':len(gold),
             'train_sha256':file_hash(Path(args.data_dir)/'train.jsonl'),
             'valid_sha256':file_hash(Path(args.data_dir)/'valid.jsonl'),
             'test_sha256':file_hash(gold_file),
             'device':device,
             'gpu':torch.cuda.get_device_name(0) if device=='cuda' else ('Apple MPS (unified memory)' if device=='mps' else platform.processor()),
             'gpu_count_available':torch.cuda.device_count(),
             'precision':str(dtype),'python':platform.python_version(), 'torch':torch.__version__,
             'baseline':baseline['metrics']}
    import transformers as _transformers, trl as _trl, peft as _peft, datasets as _datasets
    metrics['package_versions']={'transformers':_transformers.__version__,'trl':_trl.__version__,'peft':_peft.__version__,'datasets':_datasets.__version__}
    if not args.skip_training:
        peft=None
        if args.mode!='full':
            peft=LoraConfig(r=args.rank,lora_alpha=args.rank*2,lora_dropout=0.05,bias='none',task_type='CAUSAL_LM',target_modules=['q_proj','v_proj'])
        sft=SFTConfig(
            output_dir=str(work/'checkpoint'),max_steps=args.steps,
            per_device_train_batch_size=args.batch_size,per_device_eval_batch_size=1,
            gradient_accumulation_steps=args.gradient_accumulation,
            learning_rate=1e-5 if args.mode=='full' else 2e-4,
            lr_scheduler_type='cosine',warmup_steps=max(1,int(args.steps*0.05)),
            max_length=args.max_length,completion_only_loss=True,
            fp16=(device=='cuda' and dtype==torch.float16),bf16=(device=='cuda' and dtype==torch.bfloat16),
            gradient_checkpointing=True,gradient_checkpointing_kwargs={'use_reentrant':False},
            save_strategy='no',eval_strategy='no',
            logging_steps=10,report_to='none',seed=args.seed,
            dataset_text_field='text',packing=False)
        trainer=SFTTrainer(model=model,args=sft,train_dataset=Dataset.from_list(train),
                           eval_dataset=Dataset.from_list(valid),processing_class=tokenizer,
                           peft_config=peft)
        result=trainer.train()
        metrics['train_loss']=round(float(result.training_loss),6)
        validation_metrics=trainer.evaluate()
        metrics['validation_loss']=round(float(validation_metrics.get('eval_loss',float('nan'))),6)
        metrics['training_runtime_s']=round(float(result.metrics.get('train_runtime',0)),2)
        metrics['trainable_parameters']=sum(p.numel() for p in trainer.model.parameters() if p.requires_grad)
        # Quantized adapter checkpoints are small. Full-model checkpoints can be ~1GB; save explicitly only when requested.
        if args.mode!='full':
            trainer.save_model(str(work/'adapter'))
            tokenizer.save_pretrained(str(work/'adapter'))
            metrics['saved_artifact']='adapter'
        else:
            metrics['saved_artifact']='not_saved_full_to_reduce_storage'
        tuned=judge_predictions(trainer.model,tokenizer,gold,device,max_items=args.eval_max)
        (work/'tuned.json').write_text(json.dumps(tuned,indent=2,ensure_ascii=False)+'\n')
        metrics['tuned']=tuned['metrics']
    if device=='cuda':
        metrics['max_cuda_memory_gb']=round(torch.cuda.max_memory_allocated(0)/1024**3,3)
    elif device=='mps' and hasattr(torch,'mps'):
        metrics['max_mps_memory_gb']=round(torch.mps.driver_allocated_memory()/1024**3,3)
    metrics['wall_time_s']=round(time.monotonic()-start,2)
    (work/'summary.json').write_text(json.dumps(metrics,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps(metrics,indent=2,ensure_ascii=False))
    return metrics


if __name__=='__main__':main()
