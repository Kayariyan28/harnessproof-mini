---
name: Synthetic Data Lab
 description: Build and audit task-specific synthetic JSONL datasets with prompt taxonomy, seed generation, provenance, teacher constraints, holdouts and release gates.
---

# Synthetic Data Lab

## Contract

Student output is one JSON object with exactly `action`, `tool`, `arguments`, `context_strategy`, `reason`. Tools: retrieve/search_docs; calculate/calculator; clock/clock_utc; answer/none; clarify/none; refuse/none. Import `harnessproof.contracts` to validate labels; never maintain a second incompatible schema.

## Method

1. Read `data/seed_scenarios.jsonl`, `harnessproof/dataset.py`, `docs/EXPERIMENT_PROTOCOL.md`. Keep original labels/source fixed.
2. Build baseline with `python -m harnessproof.cli build-data`. Check `manifest.json` and verify 90 scenario seeds are only an educational pilot.
3. If and only if the selected OpenCode model is free at current quota, run `python -m harnessproof.cli augment --model "$OPENCODE_MODEL" --max-seeds 10 --variants-per-seed 2 --confirmed-zero-cost`. It uses the configured `opencode run` teacher; it does NOT call paid DeepSeek API directly.
4. **Improve diversity**: Generate fundamentally new domain/task families and annotate them with schema, action, taxonomy, provenance, and split. Distribute by *family* to prevent leakage; keep 10–20% test untouched. The original `build_dataset()` only augments paraphrases, so do not equate 500 paraphrases with 500 independent training cases.
5. Include counterexamples: false retrieval requirements, calculator attacks, malicious retrieved text, ambiguous inputs, time-based questions, oversized context, no-tool tasks, poor citations. Never execute hostile strings; quote them only as untrusted samples when permitted.
6. Review a stratified random sample manually and record annotation agreement/uncertainty. Reject changes in numbers, hidden action changes, same normalized prompt, ungrounded references and template-only variations.
7. Run `python -m scripts.quality_gate --mode pilot`, then `--mode publish` only when candidate dataset is substantial. Passing schema gate is NOT semantic validation.
8. Update `docs/DATA_CARD.md`: number of unique families, source/teacher model, generator version, licensing status, audit counts, limitations, train-valid-test construction, and contamination risks.

Never use teacher-labeled examples in the final held-out test. Never quote unreleased copyrighted material or personal information in the public synthetic dataset.
