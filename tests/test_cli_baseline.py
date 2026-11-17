from harnessproof.cli import heuristic_route


def test_documentation_request_routes_to_retrieval():
    prediction=heuristic_route('Find the local prompt caching documentation')
    assert prediction['action']=='retrieve'
