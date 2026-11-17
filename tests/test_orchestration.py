import pytest
from harnessproof.orchestration import ProviderRouter, Endpoint


def test_router_enforces_user_free_only_and_call_cap():
    router=ProviderRouter([Endpoint('stub-free','demo',free_verified=True)], max_requests=2)
    calls=[]
    answer=lambda p,m: calls.append((p,m)) or 'ok'
    assert router.call('stub-free',[{'role':'user','content':'test'}],answer)=='ok'
    assert router.call('stub-free',[{'role':'user','content':'test2'}],answer)=='ok'
    with pytest.raises(RuntimeError,match='quota'):router.call('stub-free',[],answer)
    assert len(calls)==2


def test_router_never_falls_back_to_paid_provider():
    router=ProviderRouter([Endpoint('paid','demo',free_verified=False)],max_requests=2)
    with pytest.raises(PermissionError,match='not verified free'):
        router.call('paid',[],lambda p,m:'not called')
