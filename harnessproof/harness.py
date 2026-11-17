"""Four bounded agent roles: router, retriever, executor/writer, verifier."""
import ast
import datetime
from pathlib import Path
from .contracts import parse_decision, validate_decision, validate_expression
from .retrieval import Retriever
from .safety import screen_request


def safe_calculate(expression):
    validate_expression(expression)
    tree=ast.parse(expression,mode='eval')
    def evaluate(node):
        if isinstance(node,ast.Expression):return evaluate(node.body)
        if isinstance(node,ast.Constant):return node.value
        if isinstance(node,ast.UnaryOp):
            x=evaluate(node.operand);return x if isinstance(node.op,ast.UAdd) else -x
        if isinstance(node,ast.BinOp):
            a,b=evaluate(node.left),evaluate(node.right)
            if isinstance(node.op,ast.Add):v=a+b
            elif isinstance(node.op,ast.Sub):v=a-b
            elif isinstance(node.op,ast.Mult):v=a*b
            elif isinstance(node.op,ast.Div):v=a/b
            elif isinstance(node.op,ast.FloorDiv):v=a//b
            elif isinstance(node.op,ast.Mod):v=a%b
            elif isinstance(node.op,ast.Pow):
                if abs(b)>10:raise ValueError('Exponent too large')
                v=a**b
            else:raise ValueError('Unsupported arithmetic')
            if abs(v)>1e12:raise ValueError('Result too large')
            return v
        raise ValueError('Invalid arithmetic node')
    try: v=evaluate(tree)
    except (ZeroDivisionError,OverflowError) as e:raise ValueError('Unsafe arithmetic') from e
    return f'{v:g}' if isinstance(v,float) else str(v)


def compact_context(text,max_chars=2400):
    """Hard character budget, NOT an exact token counter."""
    if max_chars<32:raise ValueError('Budget too small')
    if len(text)<=max_chars:return text
    head=(max_chars-24)//2
    tail=max_chars-24-head
    return text[:head]+'\n...[context trimmed]...\n'+text[-tail:]


def execute_pipeline(request,decision,knowledge_dir='docs/knowledge',writer=None, max_context_chars=2400):
    d=validate_decision(decision) if isinstance(decision,dict) else parse_decision(decision)
    trace=[{'agent':'router','action':d['action'],'tool':d['tool'],'context_strategy':d['context_strategy']}]
    blocked=screen_request(request)
    if blocked:
        if d['action']!='refuse':
            trace.append({'agent':'safety_screen','category':blocked,'overrode':d['action']})
        d={'action':'refuse','tool':'none','arguments':{},'context_strategy':'none','reason':'Blocked by deterministic safety screen.'}
    sources=[]
    action=d['action']
    if action=='calculate':
        result=safe_calculate(d['arguments']['expression'])
        answer=f'Calculated result: {result}'
        trace.append({'agent':'executor','tool':'calculator','result':result})
    elif action=='clock':
        result=datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')
        answer=f'Current UTC time: {result}'
        trace.append({'agent':'executor','tool':'clock_utc','result':result})
    elif action=='retrieve':
        hits=Retriever.from_directory(knowledge_dir).search(d['arguments']['query'],k=2)
        sources=[hit.doc_id for hit in hits]
        trace.append({'agent':'retriever','query':d['arguments']['query'],'source_ids':sources})
        if not hits:
            answer='No matching evidence was found in the local reference documents.'
        else:
            evidence='\n\n'.join(f'[{h.doc_id}] {compact_context(h.text,750)}' for h in hits)
            if writer:
                try:
                    answer=writer(request,compact_context(evidence,max_context_chars),sources)
                    trace.append({'agent':'writer','provider':'llm'})
                except Exception as e:
                    trace.append({'agent':'writer','error':type(e).__name__})
                    answer=''
            else: answer=''
            if not answer or not any(f'[{sid}]' in answer for sid in sources):
                # Attribution fallback: excerpts, not claimed interpretive conclusions.
                answer='Relevant excerpts from local documents:\n'+evidence
                trace.append({'agent':'writer','provider':'grounded_excerpt_fallback'})
    elif action=='clarify': answer='Please provide the missing document, target, or specific requirement so I can proceed safely.'
    elif action=='refuse': answer='That action is outside this harness’s permitted tools. I cannot execute it.'
    else: answer='I can explain the approach, but this demo agent does not have enough verified evidence to assert task-specific facts.'
    verified=verify_answer(answer,sources,action)
    trace.append({'agent':'verifier',**verified})
    return {'request':request,'decision':d,'answer':answer,'sources':sources,'verification':verified,'trace':trace}


def verify_answer(answer,sources,action):
    # Checks structural grounding only. Does not claim semantic factual correctness.
    refs=set(__import__('re').findall(r'\[([\w-]+)\]',answer))
    grounded=(not refs or refs.issubset(set(sources)))
    has_citation=(action!='retrieve' or not sources or bool(refs))
    return {'passed':bool(answer.strip()) and grounded and has_citation,'grounded_citation_ids':grounded,'citation_present_if_retrieved':has_citation,'semantic_factuality_checked':False}
