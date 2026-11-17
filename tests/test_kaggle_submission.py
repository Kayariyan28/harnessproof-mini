import json
import pytest
from scripts.prepare_kaggle import create_submission


def test_prepare_kaggle_creates_private_gpu_notebook(tmp_path):
    result=create_submission('https://github.com/alice/harnessproof-mini.git','alice123',tmp_path)
    meta=json.loads((tmp_path/'kernel-metadata.json').read_text())
    notebook=json.loads((tmp_path/'cloud_gpu_lab.ipynb').read_text())
    text=''.join(''.join(c['source']) for c in notebook['cells'])
    assert meta['id']=='alice123/harnessproof-mini-lab'
    assert meta['is_private'] is True
    assert meta['enable_gpu'] is True
    assert 'github.com/alice/harnessproof-mini.git' in text
    assert 'REPO_URL = "https://github.com/YOUR_ACCOUNT/harnessproof-mini.git"' not in text
    assert result['status']=='prepared_only'


def test_rejects_non_github_repo_or_bad_user(tmp_path):
    with pytest.raises(ValueError): create_submission('https://bad.site/repo.git','user',tmp_path)
    with pytest.raises(ValueError): create_submission('https://github.com/u/repo.git','../evil',tmp_path)
