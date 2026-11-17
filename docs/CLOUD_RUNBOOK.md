# Zero-local-dependency cloud runbook

**Cloud components:** GitHub Codespaces browser terminal = OpenCode + DeepSeek provider + code QA; Colab Free/Kaggle GPU notebook = training/evaluation; GitHub = public evidence; optional Hugging Face Hub = adapter artifact. All model weights and environments remain remote.

## Cloud setup checks

- GitHub personal accounts have a limited Codespaces included compute/storage quota. Check `https://github.com/settings/billing/summary`; select 2-core standard; stop codespace when idle. Larger cores can consume included credits faster. Codespaces has no NVIDIA GPU for this project.
- On Colab Free, select Runtime → Change runtime type → T4 GPU **if available**. Verify with `!nvidia-smi`. Availability and limits are not guaranteed. On Kaggle, verify account/phone requirements, enable Internet and available free GPU accelerator under notebook settings.
- OpenCode is free software, but its DeepSeek inference route can be metered. Verify the provider/model in `/models` or `opencode models`; connect only a free route if zero cash is mandatory. Do not use a card-backed API without a hard budget cap.
- **Do not install PyTorch transformer model caches on the Mac or in Codespaces.** The notebook installs large packages and downloads the model only into the remote GPU runtime.

## Starting from the delivered archive

Create a new GitHub repository, open its Codespace and upload/unzip the small archive using the browser UI. Move **hidden directories** (`.opencode`, `.devcontainer`, `.github`) alongside normal project files. With `unzip -l harnessproof-mini.zip`, inspect paths before extracting. In the repository root, the expected location of `AGENTS.md` is `./AGENTS.md`.

The main prompt is `MASTER_EXECUTION_PROMPT.md`. The skills live at `.opencode/skills/<id>/SKILL.md`. For known credentials configure **Codespaces secrets** under GitHub Settings, not in `.env` tracked files. In the hosted terminal, execute the CPU checks from README.

## Zero-bill default

- Run offline dataset builder, heuristic baseline, bounded agent tool tests, offline cache and CI without any LLM calls.
- Teacher calls are capped and opt-in after verifying DeepSeek provider cost. If DeepSeek isn't free, record blocked and continue offline; never silently substitute a paid model.
- GPU calls have finite allotted time and may be interrupted. Use 0.5B model, short context (512 tokens) and 40 steps pilot.
- Keep final reports small, delete unneeded temporary checkpoints, export **only** adapter if model performance merits release.

## Public GitHub evidence

After test suite passes, run from Codespaces:

```bash
# Only in a user-owned repository, after reviewing changes:
git status
git add AGENTS.md MASTER_EXECUTION_PROMPT.md .opencode .devcontainer .github \
  README.md LICENSE pyproject.toml requirements-cloud.txt harnessproof scripts notebooks docs data
# verify staged files show no credentials, caches or model blobs
git diff --cached --stat
git commit -m "Initial HarnessProof reproducible cloud AI lab"
git push origin HEAD
```

GitHub upload of **source**, test suites, audit methodology and small inspected metrics is the public evidence; downloading or training the large model is not necessary on the Mac.

## Colab and Kaggle

Notebook: `notebooks/cloud_gpu_lab.ipynb`. Change `REPO_URL` to public GitHub repo. Select free GPU and run cells one at a time. It clones the repository in remote temporary storage, installs cloud dependencies, builds pilot data and runs QLoRA. Run second method only if quota permits.

**Persistence:** `runs/cloud/qlora/summary.json` and `runs/cloud/qlora/adapter/` are in ephemeral cloud storage. The final notebook cell prints a small summary and points to your optional cloud export. Never assume they survive runtime shutdown.

**Failure policies:** No GPU → mark blocked; 402/429 or free quota exhausted → stop teacher/provider calls; OOM → reduce context/batch/model size; missing dependency → inspect version error then fix using tests, do not blindly upgrade everything; poor model accuracy → report measured failure and improve dataset; never invent success.
