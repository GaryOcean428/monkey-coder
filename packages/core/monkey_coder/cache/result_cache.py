from __future__ import annotations
from typing import Any, Dict, Optional
import hashlib
import json
from .base import TTLRUCache

class ResultCache:
    def __init__(self, max_entries: int = 256, default_ttl: float = 120.0):
        self._cache = TTLRUCache(max_entries=max_entries, default_ttl=default_ttl)

    @staticmethod
    def _stable_key(prompt: str, persona: str, provider: Optional[str] = None, model: Optional[str] = None, extra: Optional[Dict[str, Any]] = None) -> str:
        payload = {
            "p": prompt,
            "persona": persona,
            "provider": provider,
            "model": model,
            "extra": extra or {},
        }
        raw = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(raw.encode()).hexdigest()

    def get(self, prompt: str, persona: str, provider: Optional[str] = None, model: Optional[str] = None, extra: Optional[Dict[str, Any]] = None) -> Optional[Any]:
        key = self._stable_key(prompt, persona, provider, model, extra)
        return self._cache.get(key)

    def set(self, prompt: str, persona: str, value: Any, provider: Optional[str] = None, model: Optional[str] = None, extra: Optional[Dict[str, Any]] = None):
        key = self._stable_key(prompt, persona, provider, model, extra)
        self._cache.set(key, value)

    def stats(self) -> Dict[str, Any]:
        return self._cache.stats()

    def clear(self):
        self._cache.clear()
