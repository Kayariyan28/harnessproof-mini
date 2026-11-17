from harnessproof.retrieval import Retriever

def test_retriever_has_grounded_sources():
    engine = Retriever.from_directory('docs/knowledge')
    results = engine.search('How does prompt caching reuse repeated prefixes?', k=2)
    assert results
    assert any('caching' in r.text.lower() for r in results)
    assert results[0].doc_id and results[0].score > 0
