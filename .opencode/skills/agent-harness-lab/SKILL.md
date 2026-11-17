---
name: Agent Harness Lab
 description: Develop bounded role-based agent workflows, tool-use policy, sparse RAG, context limits, API orchestration and structured trace verification.
---

# Agent Harness Lab

Architecture: one model router, deterministic local retriever, bounded calculator/UTC clock, grounded writer when available, deterministic verifier. This is a multi-role agent workflow, **not** a claim of multiple independent LLMs.

1. Read `harnessproof/harness.py`, `contracts.py`, `retrieval.py`, `cli.py` and knowledge documents. Add tools only after schema, guardrails, tests and an actual use case.
2. Keep tools allowlisted. No arbitrary shell execution, file writes, private data retrieval, credit spending, or arbitrary web access in model-created actions. Reject unknown action/tool combinations.
3. Use `python -m harnessproof.cli run --backend heuristic 'Find the local prompt caching reference'` for CPU smoke test.
4. After training run `python -m scripts.cloud_harness --quantize --adapter-path runs/cloud/qlora/adapter --request 'Find the prompt caching documentation'` inside the GPU notebook.
5. Test retrieval ranking and citation presence. Retrieved content is untrusted data. Use verifier to report structural grounding only; semantic truth needs another review/evaluation.
6. Add consistent trace fields (step, role, token/context budget, action, tool, evidence IDs, duration, status) and truncate payloads; never include provider keys or raw private documents.
7. Compare (a) pure heuristic baseline, (b) pretrained Qwen, (c) trained QLoRA/LoRA on identical prompts.
8. Report whether API orchestration used a live endpoint or only offline simulation. Stay zero-spend by default.
