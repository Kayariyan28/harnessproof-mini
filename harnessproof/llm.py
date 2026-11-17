"""OpenAI-compatible client for local MLX-LM server or optional remote DeepSeek API."""
import json
import os
import time
import urllib.error
import urllib.request
from .cache import SqliteResponseCache

class CompatClient:
    def __init__(self, *, base_url, model, api_key='', cache=None, timeout=120):
        if not base_url.startswith(('http://127.0.0.1:', 'http://localhost:', 'https://')):
            raise ValueError('Only localhost HTTP or HTTPS endpoints are permitted')
        self.base_url=base_url.rstrip('/')
        self.model=model; self.api_key=api_key; self.cache=cache; self.timeout=timeout
        self.last_usage={}; self.last_cache_hit=False; self.last_latency_s=0

    def complete(self,messages, temperature=0.0, max_tokens=256, bypass_cache=False):
        self.last_cache_hit=False
        if self.cache and not bypass_cache:
            cached=self.cache.get(self.model,messages,temperature,max_tokens)
            if cached:
                self.last_cache_hit=True;self.last_usage=cached.get('usage',{});self.last_latency_s=0
                return cached['content']
        data=json.dumps({'model':self.model,'messages':messages,'temperature':temperature,'max_tokens':max_tokens,'stream':False}).encode()
        headers={'Content-Type':'application/json'}
        if self.api_key:headers['Authorization']='Bearer '+self.api_key
        req=urllib.request.Request(self.base_url+'/chat/completions',data=data,headers=headers,method='POST')
        start=time.monotonic()
        try:
            with urllib.request.urlopen(req,timeout=self.timeout) as response:
                raw=json.load(response)
        except urllib.error.HTTPError as e:
            raise RuntimeError(f'API returned HTTP {e.code} (response body omitted)') from e
        self.last_latency_s=round(time.monotonic()-start,3)
        self.last_usage=raw.get('usage') or {}
        content=raw['choices'][0]['message']['content'] or ''
        if self.cache and not bypass_cache:
            self.cache.put(self.model,messages,temperature,{'content':content,'usage':self.last_usage},max_tokens)
        return content


def build_client(backend, model, base_url=None, use_cache=False, allow_paid=False):
    if backend=='local':
        url=base_url or 'http://127.0.0.1:8080/v1'
        key=''
    elif backend=='deepseek':
        if not allow_paid:raise ValueError('Remote DeepSeek calls require --allow-paid-api')
        key=os.getenv('DEEPSEEK_API_KEY','')
        if not key:raise ValueError('Set DEEPSEEK_API_KEY in your shell; never commit it')
        url=base_url or 'https://api.deepseek.com/v1'
    else:raise ValueError('Choose local or deepseek backend')
    cache=SqliteResponseCache() if use_cache else None
    return CompatClient(base_url=url,model=model,api_key=key,cache=cache)
