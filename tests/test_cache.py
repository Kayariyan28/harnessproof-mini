from harnessproof.cache import SqliteResponseCache

def test_cache_keys_bind_model_and_messages(tmp_path):
    cache = SqliteResponseCache(tmp_path / 'cache.db')
    a = [{'role':'system','content':'A'},{'role':'user','content':'hi'}]
    b = [{'role':'system','content':'B'},{'role':'user','content':'hi'}]
    cache.put('local-model', a, 0.0, {'content':'hello'})
    assert cache.get('local-model', a, 0.0)['content'] == 'hello'
    assert cache.get('new-model', a, 0.0) is None
    assert cache.get('local-model', b, 0.0) is None
