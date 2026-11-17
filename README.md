# HarnessProof Mini

**OpenCode/DeepSeek-guided research on small fine-tuned AI tool routers, synthetic dataset quality, RAG, multi-role agents, prompt caching, and honest evaluation.**

Status: **local research prototype with measured results**. CPU tests, an expanded 210-example training set and two local Apple-Silicon adapters have run: fp32 LoRA reaches **88.9% held-out routing** (100% valid JSON, 3/3 refusals), the 4-bit MLX QLoRA-equivalent reaches **83.3%**, and the best hand-coded heuristic reaches **94.4%**. Base models score 0–11%. Cloud QLoRA and paid teacher expansion have **not** run. Do not describe this as a production or validated general model.

## About this project, in plain terms

**The problem.** A large AI model can do almost anything, but it is expensive and hard to control. Most real systems do not need a genius in every step. They need a cheap, predictable **dispatcher** that looks at a request and decides what should happen next: look something up, do the math, check the time, answer directly, ask for missing details, or refuse because the request is unsafe.

**The analogy.** Think of a receptionist at a small office. The receptionist does not solve every problem personally. They route each visitor to the right desk, and they are allowed to say "I need more information" or "I can't help with that." That is exactly the job this project gives a 0.5-billion-parameter language model.

| If the request… | The router decides… | Tool it may use |
|---|---|---|
| needs our own reference documents | look it up | `search_docs` |
| contains arithmetic | calculate it | `calculator` |
| asks for the current time | check the clock | `clock_utc` |
| asks for stable general knowledge | answer directly | none |
| is missing a document, number or target | ask a clarifying question | none |
| asks for secrets, destructive commands or forbidden access | refuse | none |

The model always replies with **one small JSON object**: what it wants to do, which tool (if any), the arguments, and a short public reason.

```
User request
     │
     ▼
Deterministic safety screen ──── blocked ────▶ Refuse (no tool runs)
     │ allowed
     ▼
0.5B router
     ├── retrieve ──▶ search local documents ──▶ writer ──▶ citation verifier
     ├── calculate ─▶ safe calculator
     ├── clock ─────▶ UTC clock
     └── answer / clarify / refuse ──▶ reply
```

**What we actually built**

1. **A small teaching set.** 210 training examples, 18 validation examples and 18 test examples, written as request → correct decision. The test families never appear in training, so the score is not memorisation.
2. **A student model.** Qwen2.5-0.5B is taught with LoRA on a Mac. One path uses normal 32-bit weights; the other uses a 4-bit compressed base with MLX, the closest free substitute for QLoRA because bitsandbytes needs an NVIDIA GPU.
3. **A guard-railed harness.** Routing is only one role. Separate functions retrieve evidence, execute the chosen tool, draft an answer, and verify that the answer cites real sources. A tiny model is not trusted to police itself.
4. **A bouncer in front.** A fixed, non-learned safety screen blocks credential theft and destructive commands before the model can route them to a tool. It does not depend on the model being smart that day.
5. **An honest scoreboard.** Base model, trained model and hand-written rules all answer the same 18 held-out questions, and every failure is published.

**What we found, without the jargon**

- The untrained model does not follow the format at all — it writes prose instead of JSON.
- After training it follows the format **100% of the time** and gets **83–89%** of routing decisions right.
- A simple hand-written rule set still wins on this small test (**94.4%**). That is a useful result, not a failure to hide: it tells us the task is still easy enough for rules and that 210 examples are not enough to prove a model advantage.
- The trained model still makes real mistakes, including confusing "look it up" with "answer directly" and "ask a question" with "refuse".
- The verifier caught the tiny model inventing citations, and the harness replaced the bad answer with quoted evidence instead of shipping a confident lie.

**What this is not.** It is not a chatbot, not a general assistant, not a production safety system, and not evidence that small models beat rules. It is a small, reproducible study of one narrow component, with the failures left visible.

**Why bother.** The pattern — narrow task, fixed output, real tools, deterministic guardrails, family-disjoint test, published failures — is reusable for any agent that must make a bounded decision. Everything here runs on one Mac with no paid API and no cloud account.

## Technology stack and cost boundaries

Everything used here is free or already owned: no paid API, no cloud GPU account, and no base weights in git. The table below shows where each part runs.

| Layer | Open tool | Where it runs | Cost rule |
|---|---|---|---|
| Development/teacher | [OpenCode](https://opencode.ai/) + configured DeepSeek or approved free alternative | Browser-hosted GitHub Codespaces | Free quota only; DeepSeek API may be paid |
| Code/CI | Python, pytest, GitHub Actions | Browser-hosted Codespaces + GitHub | Free personal quotas |
| Cloud training | [TRL](https://huggingface.co/docs/trl/), Transformers, PEFT, bitsandbytes | [Colab Free](https://colab.research.google.com/) or [Kaggle](https://www.kaggle.com/code) GPU | Free accelerator if allocated |
| Local training (workaround) | TRL, Transformers, PEFT on Metal/MPS | Apple Silicon Mac | No cash; ~1 GB model download, fp32 LoRA only |
| Local 4-bit training | MLX + 4-bit Qwen2.5-0.5B | Apple Silicon Mac | No cash, no account; QLoRA-equivalent, not bitsandbytes |
| Student | `Qwen/Qwen2.5-0.5B-Instruct` | Cloud GPU or Apple Silicon | Open-weight base; check base license |
| RAG/tools | Lightweight Python package in this repo | Codespaces CPU or cloud GPU | No inference bill for heuristic path |
| Caching | SQLite response cache; optional provider prefix cache | Codespaces CPU | Provider test opt-in |
| Publication | GitHub source; optional Hugging Face adapter | Cloud | No base-weight upload to GitHub |

**Zero cash spend is an experiment constraint, not a service-level guarantee.** Free GPUs are limited/unavailable at times. Codespaces consumes a monthly quota. DeepSeek's official API is not assumed free. OpenRouter's `:free` selection is rate-limited and may change. No paid fallback is enabled.

## Objective and measured outcome

**Question:** can a 0.5B open model learn a narrow, safe tool-routing contract from about 200 synthetic examples, and does it beat a transparent hand-coded heuristic?

**Setup:** family-disjoint 210 train / 18 validation / 18 test; six balanced actions; validation-loss checkpoint selection; one fixed test set; same prompts and parser for every method. All numbers below are measured, not projected.

| Router (held-out test, 18 items) | Valid JSON | Route accuracy | Refusal recall |
|---|---:|---:|---:|
| Hand-coded heuristic | 100% | **94.4%** | 2/3 |
| Base Qwen2.5-0.5B, fp32 | 0% | 0% | 0/3 |
| Base Qwen2.5-0.5B, 4-bit | 16.7% | 11.1% | 0/3 |
| LoRA fp32, 200 steps (MPS) | 100% | 88.9% | 3/3 |
| 4-bit QLoRA-equivalent, 400 iters (MLX) | 100% | 83.3% | 3/3 |

**What this shows**

- Fine-tuning reliably teaches the JSON contract: base models fail it, tuned models hit 100% valid JSON.
- The 0.5B student gets close to but does **not** beat the heuristic at this scale. 18 items means one item is 5.6 points; none of these gaps is statistically meaningful.
- 4-bit MLX is the only zero-account 4-bit path here. It is a QLoRA-equivalent (4-bit base + LoRA), **not** bitsandbytes QLoRA. At 400 iterations it reaches 83.3% with a 34 MB adapter and under 1 GB peak memory, still trailing fp32 LoRA.
- Safety remains layered: a deterministic pre-screen blocks credential and destructive patterns before any tool call, independent of model accuracy.

**What it does not show:** production readiness, general tool-routing ability, or that synthetic self-authored data is release-grade. Human audit is still missing. Details and failures: [experiment results](docs/reports/EXPERIMENT_RESULTS.md), [phase status](docs/reports/PHASE_STATUS.md), [model card](docs/MODEL_CARD.md), [data card](docs/DATA_CARD.md).

## Browser-only start: GitHub Codespaces + OpenCode

1. Make a new empty **user-owned** GitHub repo, e.g. `harnessproof-mini`. Open its **Code → Codespaces → Create codespace** browser environment. Personal free quota rules apply.
2. Upload the provided `harnessproof-mini.zip` into the browser Codespaces Explorer (drag/drop or context-menu upload). This is a one-time small archive transfer; no local software, model download or GPU is required. From the Codespaces terminal, extract the ZIP into the repository root. If a top-level folder is present, copy its *contents*, including `.opencode`, `.github`, and `.devcontainer`, into the root. Reopen Codespaces in the devcontainer after `.devcontainer/devcontainer.json` is present so OpenCode and Python dependencies are installed automatically.
3. Or, after you've committed the extracted files once, simply **clone or open your own repo** from Codespaces on subsequent sessions. Do not repeatedly upload ZIP files.
4. Configure OpenCode in Codespaces using `/connect`, select your existing DeepSeek-compatible provider, then verify the exact configured model with `opencode models`. Verify **that specific model/route is free** before teacher augmentation. If the model isn't free, complete the offline experiment and avoid paid calls.
5. Run the default zero-provider-call checks in Codespaces:

```bash
python -m pip install -e '.[dev]'
python -m pytest -q
python -m harnessproof.cli build-data
python -m scripts.quality_gate --mode pilot
python -m harnessproof.cli evaluate --backend heuristic --out runs/eval_heuristic.json
python -m scripts.benchmark_cache --mode offline
python -m scripts.audit_project
```

6. Ask OpenCode to execute the complete brief, which auto-discovers the seven skills under `.opencode/skills/`:

```bash
opencode models
opencode run --agent build --file MASTER_EXECUTION_PROMPT.md \
  "Read AGENTS.md and the attached brief, load project-orchestrator skill, and execute the phases with truthful evidence. No paid APIs or unapproved publication."
```

For optional synthetic paraphrase generation using a **verified free** OpenCode model:

```bash
export OPENCODE_MODEL='provider/your-verified-free-deepseek-route'
python -m harnessproof.cli augment --model "$OPENCODE_MODEL" \
  --max-seeds 10 --variants-per-seed 2 --confirmed-zero-cost
python -m harnessproof.cli build-data --variants data/teacher_variants.jsonl
python -m scripts.quality_gate --mode pilot
```

The teacher command makes model requests. It must **not** run merely because `OPENCODE_MODEL` was set; check price and quota first. The initial 90 manually authored synthetic seeds are small **pilot** material (54 train, 18 validation, 18 test). The `--mode publish` gate requires at least 200 training examples and additional provenance/human review before publication as a refined dataset.

## Fully OpenCode-orchestrated Kaggle alternative

If you prefer OpenCode to prepare and submit the remote GPU job rather than personally clicking Colab cells, use the **official Kaggle CLI** entirely inside Codespaces. After authenticating Kaggle (only with free GPU access), the `kaggle-cloud-runner` skill executes:

```bash
python -m pip install kaggle
python -m scripts.prepare_kaggle \
  --repo-url https://github.com/YOUR_GITHUB_USERNAME/harnessproof-mini.git \
  --kaggle-user YOUR_KAGGLE_USERNAME
kaggle kernels push -p runs/kaggle_submit --accelerator NvidiaTeslaT4
kaggle kernels status YOUR_KAGGLE_USERNAME/harnessproof-mini-lab
kaggle kernels output YOUR_KAGGLE_USERNAME/harnessproof-mini-lab \
  --file-pattern '.*summary\.json$' -p runs/kaggle_results
```

The preparation step is offline; `kaggle kernels push` makes the real remote GPU submission and must be authorized. The generated Kaggle notebook is private by default. The source repo must be public so Kaggle can clone it without secrets. The Kaggle account and API/GPU/internet permissions may still require manual browser setup; do not claim end-to-end automation was verified until real results return. See [Kaggle automation runbook](docs/KAGGLE_AUTOMATION.md).

## Local Apple Silicon workaround (no cloud GPU)

If free cloud GPU is unavailable, the same LoRA path can run on an Apple Silicon Mac with Metal (MPS). This deviates from the starter's cloud-only rule at the user's request: it downloads the ~1 GB base model into the local Hugging Face cache. QLoRA/4-bit is **not** possible locally because bitsandbytes needs CUDA; use fp32 LoRA.

```bash
uv venv --python 3.11 .venv-train
uv pip install --python .venv-train/bin/python -r requirements-local-mps.txt
.venv-train/bin/python -m scripts.cloud_train --mode lora --device mps \
  --steps 200 --batch-size 4 --gradient-accumulation 2 --eval-max 18 \
  --output-dir runs/local/lora200
.venv-train/bin/python -m scripts.cloud_harness --device mps \
  --adapter-path runs/local/lora200/adapter \
  --request "Find the prompt caching documentation"
```

Measured results are recorded in [Experiment results](docs/reports/EXPERIMENT_RESULTS.md). The adapter and model cache stay in `runs/` / the Hugging Face cache and are git-ignored; never commit weights.

### 4-bit QLoRA-equivalent with MLX (no CUDA, no account)

bitsandbytes QLoRA needs CUDA, but MLX can train LoRA adapters on a **4-bit quantized** base on Apple Silicon. This is the closest free substitute for the QLoRA arm; it is not bitsandbytes and must be labelled separately.

```bash
uv venv --python 3.11 .venv-mlx
uv pip install --python .venv-mlx/bin/python -r requirements-mlx.txt
python -m scripts.prepare_mlx
.venv-mlx/bin/python -m mlx_lm lora \
  --model mlx-community/Qwen2.5-0.5B-Instruct-4bit \
  --train --data data/mlx --fine-tune-type lora --num-layers 16 \
  --batch-size 4 --iters 400 --learning-rate 2e-4 --max-seq-length 512 \
  --mask-prompt --adapter-path runs/local/mlx_qlora400/adapter --seed 42
.venv-mlx/bin/python -m scripts.mlx_eval \
  --adapter-path runs/local/mlx_qlora400/adapter \
  --out runs/local/mlx_qlora400/eval_tuned.json
```

## Browser GPU stage: train QLoRA, LoRA, optional full

Open [`notebooks/cloud_gpu_lab.ipynb`](notebooks/cloud_gpu_lab.ipynb) in **Google Colab**, or copy its cells into **Kaggle** with Internet and GPU enabled. Change `REPO_URL` to your new public GitHub repo. The notebook clones the project into the **remote ephemeral notebook filesystem**; the Mac stores no model weights. Use the provided cloud script or run directly:

```bash
# IN COLAB/KAGGLE GPU ONLY, from cloned repo root
python -m pip install -r requirements-cloud.txt
python -m scripts.cloud_train --mode qlora --steps 40 --eval-max 18
python -m scripts.cloud_train --mode lora --steps 40 --eval-max 18
# Optional memory-heavy control only if free GPU quota allows:
python -m scripts.cloud_train --mode full --steps 40 --eval-max 18
```

Each run computes **pretrained baseline** and **fine-tuned** metrics on fixed test prompts. Quantized LoRA trains an adapter; full model mode does not automatically save a ~GB checkpoint. The script records model ID, dataset hashes, GPU, time, maximum allocated GPU memory and measured routing accuracy. These are example settings, not a claim of improved performance.

After QLoRA succeeds:

```bash
python -m scripts.cloud_harness --quantize \
  --adapter-path runs/cloud/qlora/adapter \
  --request "Find the prompt caching documentation"
```

The GPU environment is ephemeral. Before disconnecting, **save metrics or adapters to your approved cloud destination**. No automatic uploads occur. Keep raw model weights out of GitHub; Hugging Face adapter publication is optional and requires an explicit decision.

## Repository map

```
AGENTS.md                  OpenCode operating guardrails
MASTER_EXECUTION_PROMPT.md All phases and acceptance criteria
.opencode/skills/          Seven reusable OpenCode skills
harnessproof/              Dataset, harness, contracts, RAG, metrics, cache, teacher
scripts/cloud_train.py     Colab/Kaggle GPU fine-tuning and held-out evaluation
scripts/cloud_harness.py   Adapter inference + guarded multi-role pipeline
scripts/benchmark_cache.py Offline and optional provider prefix caching
scripts/quality_gate.py    Dataset integrity/scale checks
notebooks/cloud_gpu_lab.ipynb Remote browser GPU notebook
data/                       Pilot seed scenarios and deterministic splits
docs/                       Protocol, runbook, cards, status and evidence
.github/workflows/ci.yml   CPU-only GitHub Actions checks
```

## Research integrity and release constraints

- Compare models on identical held-out families; include accuracy, refusal recall, invalid outputs, retrieval errors, memory/time and failure examples.
- Prompt cache **response memoization** is not the same as model-provider **prefix/KV caching**.
- The 'multi-agent' architecture contains **role-specialized components**; do not claim multiple separately fine-tuned LLMs or automatic factual verification.
- Never commit cloud caches, `.safetensors`, paid tokens, API keys, private data or downloaded models.
- Code is provided with an MIT license. Base model, provider-generated outputs and derived datasets may have **separate licenses**; verify them before redistribution.
- Unproven parts and blockers are listed in `docs/reports/PHASE_STATUS.md`.

## References

- OpenCode skills: https://opencode.ai/docs/skills
- OpenCode CLI: https://opencode.ai/docs/cli/commands
- Hugging Face TRL + PEFT: https://huggingface.co/docs/trl/peft_integration
- Colab free GPU limitations: https://research.google.com/colaboratory/faq.html
- Kaggle GPU advice: https://www.kaggle.com/docs/efficient-gpu-usage
- GitHub Codespaces included usage: https://docs.github.com/en/billing/reference/product-usage-included
- OpenRouter free model library: https://openrouter.ai/collections/free-models/
