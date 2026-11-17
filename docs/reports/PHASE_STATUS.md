# Phase status — local CPU + local Metal GPU verification

Last verified: 2026-11-17. Environments: macOS 26 (Apple M4 Max, 40-core GPU, 48 GB), CPU Python 3.14.4 / `.venv`, training Python 3.11 / `.venv-train` (torch 2.15.0, MPS).

| Phase | Status | Evidence |
|---|---|---|
| P0 CPU framework | locally tested | `pytest -q` → **62 passed** |
| P0 seed dataset v0.1 | locally tested | 90 seeds, 30 family-disjoint families |
| P0 heuristic baseline | locally tested | 18 held-out, valid JSON 18/18, route accuracy 17/18 (94.44%), refusal recall 2/3 |
| P0 bounded harness | locally tested | retrieve, calculate and refuse paths exercised; verifier blocks bad citations |
| P1 teacher augmentation (paid API) | **blocked (cost)** | `opencode-go/deepseek-v4.1-flash` is metered; no paid calls made |
| P1 dataset expansion (in-session author) | locally tested | 156 train-only examples in 12 new families authored by the orchestrator (`opencode_session`); no API spend. Splits now **210 / 18 / 18**, 42 families |
| P1 human audit | **not done** | No independent reviewer; dataset is not release-grade despite passing numeric gates |
| P2 local LoRA (Apple MPS) | **locally GPU tested** | 4 configs at 40/100/200/400 steps; validation loss 0.995/0.640/**0.170**/0.172 selects 200 steps. Train loss 0.365, 433 s train / 505 s wall, 9.59 GB peak, 540,672 trainable params. Base 0% → tuned **100% valid JSON, 88.89% route accuracy, 3/3 refusal recall** |
| P2 400-step overfitting check | locally GPU tested | Validation loss rose to 0.1725; test stayed 16/18 with a different failure pair. 200 steps selected by the pre-registered rule |
| P2 4-bit MLX QLoRA-equivalent | locally GPU tested | MLX 0.32.4, 4-bit frozen Qwen2.5-0.5B, 2.933M LoRA params, 400 iters, val loss 3.380→0.165 (still falling), base 11.11% → tuned **83.33%** route, 3/3 refusals, adapter 34 MB, eval peak 0.656 GB. 200 iters was 72.22%. Not bitsandbytes |
| P2 cloud QLoRA/LoRA/full | **blocked (account)** | Kaggle/Colab/Paperspace/Lightning all require a signed-in account; no GPU is anonymous. Kaggle and Colab tabs opened but not authenticated; HF Jobs needs Pro/credits; bundle remains at `runs/kaggle_submit/` |
| P3 adapter in four-role harness | tested with adapter | 200-step router refused the browser-cookie exfiltration request; retrieval path fell back to grounded excerpts when the tiny writer failed citation checks; verifier passed only the fallback |
| P3 deterministic safety screen | locally tested | `harnessproof/safety.py` pre-screens 26 unsafe and 8 benign prompts; overrides an unsafe `retrieve` decision to `refuse` before the retriever runs; wired into `execute_pipeline` with trace evidence |
| P4 RAG + context | partially tested | Local retrieval works; tokenizer token counts still pending a GPU notebook run |
| P5 exact response caching | locally tested | 5 simulated requests, 3 hits (60%), 0 provider requests |
| P5 provider prefix cache | untested | Needs an approved free provider with reported cache metrics |
| P6 public GitHub | published + CI green | https://github.com/Kayariyan28/harnessproof-mini — CI runs `44118302458`, `44118596762`, `44122983372` passed in 14–17 s |
| P6 model/dataset cards | updated | Cards now disclose local training, self-authored data and failures |

## Integrity notes

- The held-out test set was **not** modified during expansion; valid/test files are byte-identical to v0.1.
- Checkpoint selection used validation loss only, with the rule fixed before the 400-step run. The test set was evaluated once per configuration; no adapter or data change was made in response to test errors. Because four configurations share the same 18-item test, 88.9% is an optimistic point estimate.
- The 0.5B student now refuses the browser-cookie exfiltration case, but routing safety is learned, not guaranteed; the deterministic refusal guard stays in front of it.
- Training moved from cloud to the local Mac at the user's explicit request. That is a deviation from the starter's cloud-only rule and is recorded in the model card.
- The MLX run is a 4-bit frozen base plus LoRA (QLoRA-equivalent), **not** bitsandbytes QLoRA, and must not be described as a cloud QLoRA result.

## Blockers / next

1. **Human review** of the 12 new families, especially refusal and clarify boundaries, before any release claim.
2. **Cloud QLoRA** remains untested; `runs/kaggle_submit/` is ready once Kaggle OAuth and a GPU allocation exist.
3. **bitsandbytes QLoRA remains CUDA-only.** Use the MLX 4-bit path locally and label it as a QLoRA-equivalent; it is not the same kernel or the same result.
4. **No adapter publication.** A Hugging Face release needs license review and explicit approval.
