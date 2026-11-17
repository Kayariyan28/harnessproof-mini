# Context window management

A context window limits the number of tokens an LLM can process at a time. Use retrieved excerpts instead of full documents; reserve output capacity; keep stable system instructions before volatile user content. For long histories compact or summarize old turns and preserve the latest request and critical constraints. Document every truncation.

The demo compact_context helper enforces a character ceiling rather than a tokenizer-accurate budget; actual model-token counts require the exact model tokenizer. Benchmark compaction separately so it cannot hide necessary facts. Do not equate an application's response cache with a model's KV cache.
