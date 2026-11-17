---
name: Caching and Context Lab
 description: Benchmark exact-response caching, optional provider prefix caching, token-window budgets and RAG-vs-context tradeoffs without fabricated savings.
---

# Caching and Context Lab

Separate the experiments:

- **Local exact-response cache**: `SqliteResponseCache`, keyed by model+messages+temperature+max tokens; zero provider requests; measure hit ratio, not hypothetical token cost savings.
- **Provider prefix caching**: same stable prefix + varied suffix; 3 explicit remote provider requests only if free and approved. Use `scripts/benchmark_cache.py --mode provider --model ... --base-url ... --allow-external-api`, with key in a Codespaces secret. If usage does not include cache hit counts, mark unknown.
- **Context window management**: character cap in CPU harness is NOT a token budget. On GPU notebook, count tokens with `tokenizer.encode`, record truncation, compare retrieve-only versus full context.

Experiment controls: fixed inputs, provider name, model ID, runtime, measured latency, token counts if available, hit counters, response-cache bypass for provider-side test, explicit quota/fee state. Do not claim two different provider token cache systems are directly equivalent. Never execute unbounded repeated calls or guess cost without pricing/source.
