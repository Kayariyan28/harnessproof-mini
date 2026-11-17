"""Transparent local RAG (sparse retrieval) with document IDs and no network access."""
import math
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

STOP={'the','for','and','our','are','you','what','how','does','with','from','this','that','when','have','into','about','can','use','not','your','which','is','a','an','to','in','of','on','it','we'}

def words(s): return [w for w in re.findall(r'[a-z0-9_]+',s.lower()) if w not in STOP and len(w)>1]

@dataclass
class Result:
    doc_id: str
    text: str
    score: float

class Retriever:
    def __init__(self, documents):
        self.docs=documents
        self.vocab=[Counter(words(d[1])) for d in documents]
        self.df=Counter(t for vec in self.vocab for t in vec)

    @classmethod
    def from_directory(cls, directory):
        paths=sorted(Path(directory).glob('*.md'))
        return cls([(p.stem,p.read_text(encoding='utf-8')) for p in paths])

    def search(self, query, k=3):
        q=Counter(words(query)); n=len(self.docs)
        results=[]
        for (doc_id, text),vec in zip(self.docs,self.vocab):
            score=sum((1+math.log(vec[t]))*math.log((n+1)/(self.df[t]+0.5)+1)*q[t] for t in q if vec[t]>0)
            if score>0: results.append(Result(doc_id,text,round(score,4)))
        return sorted(results,key=lambda r:(-r.score,r.doc_id))[:k]
