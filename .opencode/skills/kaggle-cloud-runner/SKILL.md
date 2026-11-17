---
name: Kaggle Cloud Runner
 description: Use the official Kaggle CLI from browser Codespaces to submit, monitor and retrieve free GPU notebook experiments without using the user's Mac.
---

# Kaggle Cloud Runner

The fully orchestrated **cloud** route is Codespaces → OpenCode/DeepSeek → `kaggle kernels push` → remote GPU notebook → `kaggle kernels status` / `output` → GitHub evidence.

1. Read `docs/KAGGLE_AUTOMATION.md` and Kaggle CLI's current help. Install Kaggle CLI only in Codespaces (cloud CPU). Verify the user has granted Kaggle access and no billing is enabled; phone verification / GPU quotas may block first launch.
2. Verify GitHub repo is public because notebook clones source without secrets. Verify Kaggle account identity. Configure auth with a Codespaces secret or Kaggle OAuth; never commit any API token.
3. `python -m scripts.prepare_kaggle --repo-url https://github.com/OWNER/harnessproof-mini.git --kaggle-user YOUR_KAGGLE_USERNAME` builds a **private** GPU notebook submission in ignored `runs/kaggle_submit/`.
4. Inspect metadata, notebook content and service quota. Only submit when authorized and within free quota: `kaggle kernels push -p runs/kaggle_submit --accelerator NvidiaTeslaT4`.
5. Use `kaggle kernels status USER/harnessproof-mini-lab` and `kaggle kernels output USER/harnessproof-mini-lab --file-pattern '.*summary\\.json$' -p runs/kaggle_results` only after run completes. Do not run infinite polling loops or multi-notebook floods.
6. Save a redacted results report to `docs/reports/EXPERIMENT_RESULTS.md`. Do not publish raw adapter or weights automatically. If notebook fails because internet is disabled or GPU absent, stop and report the exact limitation; guide user to a browser interactive Kaggle/Colab run instead.
7. Do not assume that Kaggle CLI submission has been executed merely because a notebook file exists.
