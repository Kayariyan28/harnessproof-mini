import json
import pytest
from harnessproof.contracts import validate_decision, ROUTER_PREFIX


def test_valid_retrieve():
    d = validate_decision({"action":"retrieve","tool":"search_docs","arguments":{"query":"prompt caching"},"context_strategy":"retrieve","reason":"Need local reference."})
    assert d["tool"] == "search_docs"


def test_reject_non_allowlisted_tool():
    with pytest.raises(ValueError):
        validate_decision({"action":"execute","tool":"run_shell","arguments":{"command":"rm -rf /"},"context_strategy":"none","reason":"bad"})


def test_reject_mismatch_and_invalid_expression():
    with pytest.raises(ValueError):
        validate_decision({"action":"calculate","tool":"calculator","arguments":{"expression":"__import__('os')"},"context_strategy":"none","reason":"bad"})
    assert "Return exactly one JSON" in ROUTER_PREFIX


def test_parse_markdown_fence_or_thinking():
    from harnessproof.contracts import parse_decision
    source='<think>do not expose</think>\n```json\n{"action":"clarify","tool":"none","arguments":{},"context_strategy":"none","reason":"Need an input."}\n```'
    assert parse_decision(source)["action"] == "clarify"
