"""Prepare a private Kaggle GPU notebook submission; never authenticates or submits."""
import argparse
import json
import re
from pathlib import Path

URL = re.compile(r'https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+(?:\.git)?/?\Z')
USER = re.compile(r'[A-Za-z0-9][A-Za-z0-9_-]{1,38}\Z')


def create_submission(repo_url, kaggle_user, output_dir='runs/kaggle_submit'):
    if not URL.fullmatch(repo_url):
        raise ValueError('Only https://github.com/OWNER/REPO(.git) public repository URL permitted')
    if not USER.fullmatch(kaggle_user):
        raise ValueError('Invalid Kaggle username')
    source=Path(__file__).resolve().parents[1]/'notebooks'/'cloud_gpu_lab.ipynb'
    notebook=json.loads(source.read_text(encoding='utf8'))
    patched=0
    for cell in notebook['cells']:
        if cell['cell_type']!='code':continue
        body=''.join(cell['source'])
        new,n=re.subn(r'(?m)^REPO_URL\s*=\s*"https://github.com/YOUR_ACCOUNT/harnessproof-mini.git"\s*$',
                       'REPO_URL = '+json.dumps(repo_url),body)
        if n:
            patched+=n
            cell['source']=new.splitlines(keepends=True)
        cell['outputs']=[]
        cell['execution_count']=None
    if patched!=1:
        raise ValueError('Failed to patch exactly one REPO_URL in notebook')
    path=Path(output_dir);path.mkdir(parents=True,exist_ok=True)
    (path/'cloud_gpu_lab.ipynb').write_text(json.dumps(notebook,ensure_ascii=False,indent=1)+'\n')
    slug=f'{kaggle_user}/harnessproof-mini-lab'
    meta={
        'id':slug,'title':'HarnessProof Mini Lab','code_file':'cloud_gpu_lab.ipynb',
        'language':'python','kernel_type':'notebook','is_private':True,
        'enable_gpu':True,'enable_internet':True,'machine_shape':'NvidiaTeslaT4',
        'dataset_sources':[],'competition_sources':[],'kernel_sources':[],'model_sources':[]
    }
    (path/'kernel-metadata.json').write_text(json.dumps(meta,indent=2)+'\n')
    return {'status':'prepared_only','path':str(path),'kaggle_id':slug,'gpu':'NvidiaTeslaT4',
            'note':'No Kaggle login, GPU allocation or notebook execution has occurred.'}


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--repo-url',required=True)
    p.add_argument('--kaggle-user',required=True)
    p.add_argument('--out-dir',default='runs/kaggle_submit')
    args=p.parse_args()
    print(json.dumps(create_submission(args.repo_url,args.kaggle_user,args.out_dir),indent=2))

if __name__=='__main__':main()
