# Dataset card — HarnessProof Seed Router v0.1

**Status:** PILOT, not ready for a quality-claiming general dataset release.

- Purpose: instruction tuning for bounded next-action routing in a safe agent harness.
- Source: 90 manually authored synthetic scenarios generated for this starter project (not scraped personal data). No DeepSeek-generated variants yet.
- Schema: `prompt` text + `completion` serialized exact routing JSON. Separate `.meta.jsonl` carries family, taxonomy, provenance, expected action and tool.
- Train/validation/test: 54/18/18 examples; 30 families (family-disjoint); six action categories; test examples remain unaugmented.
- Known problems: tiny dataset, formulaic language, over-simple tasks, category shortcuts, unproven transfer to realistic tool calls, no human inter-rater validation.
- Intended use: local/hosted experiments and method demonstration. Not safe for unsupervised privileged tooling.
- Privacy: samples should contain no personal data. Audit before release anyway.
- Teacher augmentation: **NOT RUN**. Any new variants must be separately labeled as teacher paraphrases with exact model/provider and generation method.
- Release prerequisites: expand to independent examples, run `python -m scripts.quality_gate --mode publish`, manual stratified review, data license/provenance verification.
