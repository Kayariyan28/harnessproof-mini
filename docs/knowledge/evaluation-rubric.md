# Agent evaluation rubric

Score held-out scenario families rather than random paraphrases of the same scenario. Core measures: valid JSON rate, route accuracy, selected-tool accuracy, retrieval recall, source attribution, refusal recall, latency, memory, and application/provider cache hits. Separately measure a base model, fine-tuned model, and deterministic baseline. An LLM judge is supplementary, not gold ground truth.

Hard failures include hallucinated tool names, unsupported side effects, arbitrary calculator execution, false document citations, secret leakage, and a model improving only on training examples. Publish sample counts, provenance, reproducible configs, and honest failures. Never claim quality improvement without measured held-out results.
