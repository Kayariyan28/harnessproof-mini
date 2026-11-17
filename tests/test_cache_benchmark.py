from scripts.benchmark_cache import offline_experiment

def test_offline_cache_reports_only_actual_simulated_hits():
    report = offline_experiment()
    assert report['provider_requests'] == 0
    assert report['cache_hits'] == 3
    assert report['hit_rate'] == 0.6
    assert 'No LLM calls' in report['qualification']
