# Dataset card — HarnessProof Seed Router v0.2

**Status:** PILOT-PLUS, expanded for local training. Numeric publish gate passes; **human audit has not been performed**, so it is not a validated public dataset.

- Purpose: instruction tuning for bounded next-action routing in a safe agent harness.
- Sources:
  - 90 curated seed scenarios from v0.1 (`human_authored_synthetic_seed`), including all validation and test items.
  - 156 additional **train-only** scenarios in 12 new families (`opencode_session`), authored in-session by the OpenCode orchestrator model. No paid teacher API was called; no provider quota was consumed.
- Schema: `prompt` text + `completion` serialized exact routing JSON. `.meta.jsonl` carries family, taxonomy, provenance, expected action and tool.
- Splits: **210 train / 18 validation / 18 test**; 42 families, family-disjoint. Validation and test are byte-identical to v0.1 and were not augmented.
- Coverage: six balanced action classes (35 each in train after expansion) and six taxonomies.
- Expansion families: `spec_lookup`, `policy_reference`, `unit_conversion_math`, `budget_arithmetic`, `sla_deadline_utc`, `schedule_utc`, `concept_explanation`, `best_practice`, `underspecified_scope`, `missing_inputs`, `credential_access`, `destructive_cli`.
- Numeric gate: `python -m scripts.quality_gate --mode publish` passes (210 ≥ 200, 42 ≥ 18 families, 6 actions, ≥10 per action).
- Known problems:
  - The expansion was written by the same model family that orchestrates the project; this is self-authored data, not independent human annotation.
  - Train-only families differ in style from the holdout families, so accuracy may reflect a distribution shift.
  - No inter-rater agreement, no stratified human review, no adversarial red-team pass.
  - Formulaic language and category shortcuts remain possible.
- Intended use: local/hosted method experiments and demonstration. Not safe for unsupervised privileged tooling.
- Privacy: no personal data. Credential-access prompts are synthetic refusal examples only; no real secrets appear.
- Release prerequisites: manual stratified review of the new families, near-duplicate audit against external sources, and license/provenance sign-off.
