from __future__ import annotations
from typing import Any, Dict, Optional
import hashlib
import json
from .base import TTLRUCache

class RoutingDecisionCache:
    def __init__(self, max_entries: int = 512, default_ttl: float = 30.0):
        self._cache = TTLRUCache(max_entries=max_entries, default_ttl=default_ttl)

    @staticmethod
    def _stable_key(prompt: str, context_type: str, complexity_bucket: str) -> str:
        payload = {
            "p": prompt[:800],  # limit size
            "ctx": context_type,
            "cx": complexity_bucket,
        }
        raw = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(raw.encode()).hexdigest()

    def get(self, prompt: str, context_type: str, complexity_bucket: str) -> Optional[Any]:
        key = self._stable_key(prompt, context_type, complexity_bucket)
        return self._cache.get(key)

    def set(self, prompt: str, context_type: str, complexity_bucket: str, decision: Any):
        key = self._stable_key(prompt, context_type, complexity_bucket)
        self._cache.set(key, decision)

    def stats(self) -> Dict[str, Any]:
        return self._cache.stats()

    def clear(self):
        self._cache.clear()
