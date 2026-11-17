# Model card — HarnessProof Mini Router

**Status:** UNTRAINED STARTER. There is currently no trained adapter included in this package.

- Intended base: `Qwen/Qwen2.5-0.5B-Instruct` (check the model's actual license before redistribution).
- Target behavior: one constrained JSON decision for tool routing (retrieve, calculate, clock, answer, clarify, refuse).
- Methods planned: LoRA rank 8, QLoRA NF4 rank 8; full-layer small-model comparison optional.
- Data: `data/processed` family-disjoint small synthetic pilot; expansion and human audit pending.
- Training environment: Colab Free/Kaggle GPU when available, never user's Mac.
- Real measured model accuracy: **PENDING GPU TRAINING**.
- Not for privileged autonomous actions, production financial/medical decisions, or unreviewed external network execution.
- Tool allowlisting, arithmetic AST validation, retrieval citation checks and external secrets policy remain enforced regardless of model predictions.
- Publication: optional Hugging Face adapter only with consent and license/provenance review. Do not upload raw base model or training private prompts.
