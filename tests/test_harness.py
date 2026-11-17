import pytest
from harnessproof.harness import safe_calculate, execute_pipeline


def test_calculator_safe():
    assert safe_calculate('12*(3+2)') == '60'
    with pytest.raises(ValueError):
        safe_calculate('open("/etc/passwd")')


def test_pipeline_retrieval_and_trace():
    route = {"action":"retrieve","tool":"search_docs","arguments":{"query":"context windows"},"context_strategy":"retrieve","reason":"Use documentation."}
    res = execute_pipeline('What is our context window policy?', decision=route, knowledge_dir='docs/knowledge')
    assert 'retriever' in [x['agent'] for x in res['trace']]
    assert res['sources']
    assert res['verification']['passed']
    assert '[' + res['sources'][0] + ']' in res['answer']


def test_pipeline_calculation():
    route = {"action":"calculate","tool":"calculator","arguments":{"expression":"9*7"},"context_strategy":"none","reason":"Arithmetic."}
    res = execute_pipeline('Compute 9 times 7', decision=route)
    assert '63' in res['answer']
    assert res['verification']['passed']
