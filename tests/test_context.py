from harnessproof.context import choose_context

class DummyTokenizer:
    def encode(self,text,add_special_tokens=False):
        return text.split()


def test_context_budget_is_tokenizer_measured():
    chunks=[('doc-one','one two three'),('doc-two','four five six')]
    result=choose_context(chunks,DummyTokenizer(),budget=5)
    assert result['used_tokens']==3
    assert result['selected']==[('doc-one','one two three')]
    assert result['excluded_ids']==['doc-two']
