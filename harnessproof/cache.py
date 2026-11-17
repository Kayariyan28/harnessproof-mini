"""Small SQLite response cache; distinct from provider-side prefix/KV caching."""
import hashlib
import json
import sqlite3
from pathlib import Path

class SqliteResponseCache:
    def __init__(self, path='runs/response_cache.sqlite', max_entries=500):
        self.path=Path(path)
        self.path.parent.mkdir(parents=True,exist_ok=True)
        self.max_entries=max_entries
        with sqlite3.connect(self.path) as c:
            c.execute('CREATE TABLE IF NOT EXISTS responses (key TEXT PRIMARY KEY, payload TEXT NOT NULL, created TEXT DEFAULT CURRENT_TIMESTAMP)')

    @staticmethod
    def key(model, messages, temperature, max_tokens=256):
        payload={'version':1,'model':model,'messages':messages,'temperature':temperature,'max_tokens':max_tokens}
        return hashlib.sha256(json.dumps(payload,sort_keys=True,ensure_ascii=False).encode()).hexdigest()

    def get(self, model, messages, temperature, max_tokens=256):
        key=self.key(model,messages,temperature,max_tokens)
        with sqlite3.connect(self.path) as c:
            row=c.execute('SELECT payload FROM responses WHERE key=?',(key,)).fetchone()
        return json.loads(row[0]) if row else None

    def put(self, model, messages, temperature, result, max_tokens=256):
        key=self.key(model,messages,temperature,max_tokens)
        with sqlite3.connect(self.path) as c:
            c.execute('INSERT OR REPLACE INTO responses (key,payload) VALUES (?,?)',(key,json.dumps(result)))
            c.execute('DELETE FROM responses WHERE key IN (SELECT key FROM responses ORDER BY created DESC,key DESC LIMIT -1 OFFSET ?)',(self.max_entries,))
