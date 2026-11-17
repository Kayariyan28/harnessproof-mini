# Model card — HarnessProof Mini Router (local LoRA v0.1)

**Status:** TRAINED LOCALLY, NOT RELEASED. An adapter exists only in the git-ignored `runs/local/` directory on the author's machine. No weights are published.

- Base model: `Qwen/Qwen2.5-0.5B-Instruct` (check the Qwen license before any redistribution).
- Adapter: LoRA rank 8, alpha 16, dropout 0.05, targets `q_proj`/`v_proj`; 540,672 trainable parameters.
- Training: Apple M4 Max Metal (MPS), fp32, **200 optimizer steps** (selected by lowest validation loss), batch 4 × gradient accumulation 2, lr 2e-4 cosine, max length 512, seed 42.
- Data: `Seed Router v0.2` — 210 train / 18 valid / 18 test, 42 family-disjoint families; 156 train examples were authored in-session by the OpenCode orchestrator (`opencode_session`), 90 are curated seeds. See `DATA_CARD.md`.
- Target behavior: one constrained JSON object for routing among `retrieve`, `calculate`, `clock`, `answer`, `clarify`, `refuse`.
- Measured on the fixed 18-item held-out set: **100% valid JSON, 88.89% route/tool accuracy, refusal recall 3/3**. Base model: 0% valid JSON. Hand-coded heuristic: 94.44%. See `reports/EXPERIMENT_RESULTS.md`.
- Selection: validation loss across 40/100/200/400 steps was 0.995/0.640/0.170/0.172; the 200-step checkpoint was selected. The test set was evaluated once per configuration and was not used to change the data or adapter.
- Known failures: "What does the internal handbook recommend for long contexts?" → `answer` instead of `retrieve`; "Briefly define a model adapter." → `clarify` instead of `answer`. The 100-step model also missed a browser-cookie exfiltration request; the 200-step model refuses it correctly in the harness. Safety is still not guaranteed, so the deterministic refusal guard stays in front.
- Intended use: research demo of bounded tool routing. Not for privileged autonomous actions, production finance/medical decisions, or unreviewed external side effects.
- Guardrails that remain independent of the model: the deterministic safety screen, tool allowlist, arithmetic AST validation, citation checks, and per-task timeouts.
- Training-environment deviation: the starter required cloud GPU only; this adapter was trained locally at the user's request because free cloud credentials were unavailable. QLoRA (4-bit) was not run because bitsandbytes needs CUDA.
- Publication: no Hugging Face upload. Any release requires a license/provenance review, redacted metrics, and explicit approval.
