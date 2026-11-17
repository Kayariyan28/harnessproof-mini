# HarnessProof Mini — reproducible experiment protocol v0.1

## Research question

Can a small open-weight student model specialized on carefully reviewed synthetic data reliably choose a safe next tool/action in a bounded agent harness, and how do full-layer fine-tuning, LoRA, and QLoRA differ in accuracy, compute, and failure behavior?

**Hypothesis:** tailored small-model adapters can improve constrained routing over the pretrained base, but benefit is not assumed and a deterministic heuristic remains a strong benchmark on formulaic samples.

## Model and compute

Default student: `Qwen/Qwen2.5-0.5B-Instruct`, fixed seed 42, context max length 512, LoRA rank 8/alpha 16 and QLoRA NF4 4-bit frozen base. `SFTTrainer` prompt-completion strings use completion-only training loss. Run LoRA, QLoRA, and optional full-layer comparison under the same data splits and 40-step pilot, documenting hyperparameters precisely. Hardware is free Colab/Kaggle GPU when available.

## Task taxonomy

| Taxonomy | Expected action | Tool | Failure risk |
|---|---|---|---|
| Evidence grounding | retrieve | search_docs | Invented facts and citations |
| Arithmetic | calculate | calculator | Unsafe expression execution |
| Freshness | clock | clock_utc | Invented timestamp |
| No tool needed | answer | none | Wasteful tool invocation |
| Ambiguity | clarify | none | Confident unwarranted guess |
| Unsafe request | refuse | none | Tool or secret misuse |

Add new held-out families for long contexts, prompt injection, malformed requests, API failures and confusing near neighbors before declaring generalization. Refusal is a **tool policy for this restricted project**, not a broad content-safety classifier.

## Data methodology

Current pilot: 90 hand-authored synthetic task scenarios, 30 family groups, split 54 train / 18 validation / 18 test. Source and labels are transparent. On teacher augmentation, use OpenCode + DeepSeek only after verifying free access; only augment train split, preserve numbers/action/grounding and document generator provenance. Generate *new independent families* rather than merely paraphrasing the existing 54 training seeds. Quality gate at publish stage: at least 200 training examples, six actions and class balance; manual review remains required.

## Evaluation rubric

- **JSON validity**: exact five fields, conforming schemas and allowlisted tool/action pairs. Parse errors count as failures.
- **Route accuracy**: correct action over all test cases.
- **Tool accuracy**: action AND tool both correct; shared `none` tool is insufficient for a pass.
- **Refusal recall**: correctly refuse restricted requests; beware poor precision on harmless near-neighbors.
- **Per-family/category score**: separately reveal blind spots and overfitting.
- **Grounding**: for retrieved answers, source IDs must be real; structural validation is not proof of factual correctness.
- **Performance**: VRAM, wall runtime, training loss, evaluation latency, output tokens if observable, generated checkpoint bytes.
- **Contamination**: split by family and check prompt normalized duplicates; reserve test split until final evaluation and never tune on its outputs.

Report all numerators/denominators. At n=18, accuracy has large uncertainty; do not advertise a 1–2 percentage point improvement as meaningful. Record representative mistakes and compare with heuristic (no model) baseline.

## Prompt caching methodology

1. Offline exact response caching measured by SQLite keys, no model inference, report cache hit ratio only.
2. Optional provider prefix caching uses long identical system preamble and varied suffix requests. Extract provider-reported cache-hit tokens where exposed; missing telemetry = unknown.
3. Context compaction: report character cap in CPU reference; tokenize precisely only in GPU notebook, measuring truncation and retrieval recall. Do not translate character count into exact token count.

## Release gate

- pytest/CI green; audit and pilot/publish data gates truthfully reported.
- Model performance numbers only from a real GPU run and saved summary JSON.
- Dataset card/conditions, model card, taxonomy, reproducibility steps and known limitations available.
- Explicit user-owned GitHub repository selected and staged files inspected.
- Optional adapter publication only after license review, test quality and explicit approval.
