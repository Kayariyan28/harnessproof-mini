"""Actual context budgeting using the selected model tokenizer, not character estimates."""


def choose_context(chunks, tokenizer, budget=512):
    if budget < 1:
        raise ValueError('Token budget must be positive')
    selected=[];excluded=[];used=0
    for doc_id,text in chunks:
        tokens=len(tokenizer.encode(text,add_special_tokens=False))
        if used+tokens<=budget:
            selected.append((doc_id,text))
            used+=tokens
        else:
            excluded.append(doc_id)
    return {'selected':selected,'used_tokens':used,'budget':budget,'excluded_ids':excluded}
