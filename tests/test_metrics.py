from harnessproof.evaluation import evaluate_predictions

def test_metrics_accuracy_and_invalid():
    examples = [{'id':'1','action':'calculate','tool':'calculator'},{'id':'2','action':'retrieve','tool':'search_docs'}]
    predictions = [{'id':'1','decision':{'action':'calculate','tool':'calculator'}},{'id':'2','error':'invalid json'}]
    results = evaluate_predictions(examples,predictions)
    assert results['total'] == 2
    assert results['valid_json_rate'] == 0.5
    assert results['route_accuracy'] == 0.5
    assert results['tool_accuracy'] == 0.5

def test_tool_accuracy_requires_correct_action_not_just_none_tool():
    examples = [{'id':'1','action':'refuse','tool':'none'}]
    predictions = [{'id':'1','decision':{'action':'answer','tool':'none'}}]
    result = evaluate_predictions(examples,predictions)
    assert result['tool_accuracy'] == 0.0
