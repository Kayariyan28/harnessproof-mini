# Kaggle CLI cloud GPU automation — OpenCode-controlled route

This is the preferred path when OpenCode must handle **submitting a cloud training run, monitoring it, and retrieving its metrics**, without local GPU use or manual browser notebook execution. It still requires the user's Kaggle identity/authentication, actual free GPU quota, and permission to submit the job. This integration is prepared but **not live-tested with Kaggle credentials**.

## Prerequisites (browser-only)

- Source archive is committed to a public repository that the cloud notebook can clone.
- GitHub Codespaces has OpenCode, Python, Git and a user-owned remote. Install official Kaggle CLI in Codespaces only: `python -m pip install kaggle`.
- User signs into Kaggle, completes any verification, and provides account credentials **only** through Codespaces secret configuration or Kaggle's official OAuth login (`kaggle auth login`) as supported in the current environment. Never copy token into a repository file or prompt.
- Check free GPU quota, Internet permissions and whether the NVIDIA T4 accelerator is available. If not, switch to browser Colab Free manually without any billable upgrade.

## Commands for OpenCode to execute in Codespaces

```bash
# From public GitHub repository root. Replace OWNER and YOUR_KAGGLE_USERNAME.
python -m scripts.prepare_kaggle \
  --repo-url https://github.com/OWNER/harnessproof-mini.git \
  --kaggle-user YOUR_KAGGLE_USERNAME

# Inspect the generated metadata, source and account quota; submission is a separate permitted action.
cat runs/kaggle_submit/kernel-metadata.json
kaggle kernels push -p runs/kaggle_submit --accelerator NvidiaTeslaT4

# Verify progress and collect small outputs after completion.
kaggle kernels status YOUR_KAGGLE_USERNAME/harnessproof-mini-lab
kaggle kernels output YOUR_KAGGLE_USERNAME/harnessproof-mini-lab \
  --file-pattern '.*summary\.json$' -p runs/kaggle_results
```

The preparation script never invokes Kaggle services; it only copies and patches the notebook and writes a **private** Kaggle kernel-metadata.json with GPU and Internet flags. If the Kaggle backend ignores Internet, clone/install may fail; report that as a blocker and use the interactive notebook browser mode. `kaggle kernels push` is the real remote job submission; request user approval for that external action.

OpenCode should read the resulting `harnessproof_qlora_summary.json` from `runs/kaggle_results`, inspect real accuracy and failure modes, write a redacted summary into `docs/reports/EXPERIMENT_RESULTS.md`, and push that small report to the already approved GitHub repo. Never commit downloaded model weights or API credentials. The private Kaggle notebook may contain outputs; review before choosing to publish Kaggle or Hugging Face artifacts.

API documentation:
- https://github.com/Kaggle/kaggle-cli/blob/main/docs/kernels.md
- https://github.com/Kaggle/kaggle-cli/blob/main/docs/kernels_metadata.md
