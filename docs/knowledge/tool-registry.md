# Approved tool registry

Allowed actions: retrieve / search_docs: arguments {"query": "keywords"}; calculate / calculator: arguments {"expression": "bounded arithmetic"}; clock / clock_utc: empty arguments; answer / none; clarify / none; refuse / none. The executor must validate all decisions before invoking tools.

No shell execution, network upload, email sending, code execution, private file reading, or browsing tool is available in the benchmark agent. Orchestrator and teacher API access are separate, explicitly configured development components, not tools granted to the task router.
