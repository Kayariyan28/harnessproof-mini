---
name: Evaluation and Release
 description: Build trustworthy rubrics, baseline-versus-adapter comparisons, benchmark reports, model/data cards, GitHub CI and public evidence with release checks.
---

# Evaluation and Release

1. Keep a 6-action confusion matrix plus per-taxonomy route accuracy, valid JSON, tool accuracy, refusal recall, citation presence, hallucinated sources, overhead and compute/memory.
2. Use untouched `test.meta.jsonl` for final evaluation. Family-disjoint test does not itself guarantee semantic novelty; record this caveat.
3. Pass `pytest`, offline evaluation, `quality_gate.py` and `audit_project.py`. The `publish` quality gate must be passed before calling the dataset release quality-controlled. Manual label review is separate and required.
4. For every table of results include model ID, training type, exact checkpoint hash/adapter version, data hash, GPU, date, inference settings, sample size and confidence caveat.
5. Prepare `docs/MODEL_CARD.md`, `docs/DATA_CARD.md`, `docs/reports/EXPERIMENT_RESULTS.md`, and reproducible commands. Use status `pending` rather than invented numbers.
6. `.gitignore` protects checkpoints but audit `git status` and staged files manually. Never push paid secrets, copyrighted/private prompts, or model base weights. Push to an explicitly selected user-owned GitHub repo; optional Hugging Face upload requires separate authorization.
7. Prefer a v0.1 release with transparent limitations rather than aggressive claims. Add a short demo, architecture diagram, and reproducibility section when actually verified.
