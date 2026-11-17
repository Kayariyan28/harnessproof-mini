---
name: Project Orchestrator
description: Coordinate the end-to-end browser-cloud HarnessProof experiment, budget limits, phases, provenance and status reports.
---

# Project Orchestrator

When coordinating this project, load `AGENTS.md` and `MASTER_EXECUTION_PROMPT.md` first. Keep a phased plan with reproducible commands and truthful gate outcomes. Never silently run a paid API, upload a model, or assume Colab GPUs are available.

1. Inspect `git status`, repo tree, configured remote, `python --version`, `opencode models`, and available quotas. Do not print credentials.
2. Establish offline baseline and unit tests before DeepSeek generation.
3. Call skills by exact IDs: `synthetic-data-lab`, `cloud-finetune`, `agent-harness-lab`, `caching-context-lab`, `evaluation-release`.
4. Use GitHub Codespaces for OpenCode orchestration and Python CPU QA; Colab/Kaggle only for GPU steps.
5. For each milestone record: command, environment, UTC time, status, observed outputs, failure logs with secrets removed, next actionable gate.
6. Only push to a verified user-controlled GitHub remote. Prepare all commits first; get explicit user approval for public repository setup and optional Hugging Face model publication.
7. Finish with supported claims and links to actual commit, notebook and metrics. Do not claim any fine-tuning performance in a planning-only run.
