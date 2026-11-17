# Prompt caching policy

Prompt caching has two distinct levels. Application-level response caching reuses an entire result for identical model, instructions, parameters and input; it must include model and prompt version in its cache key. DeepSeek's API also offers provider-side context prefix caching, based on matching identical token prefixes. Cache hits are best-effort and should be measured from usage counters such as prompt_cache_hit_tokens, not assumed.

Experiments compare cold and warm prefixes, report actual token-cache hits, response latency and error rates. Put stable instructions and shared documents before variable user questions. Never store API keys, secret values or personal documents in the public trace or repository. SQLite cache is disabled for sensitive workloads by policy.
