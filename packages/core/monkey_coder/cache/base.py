from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Optional, Dict
import time
from collections import OrderedDict

@dataclass
class CacheEntry:
    value: Any
    expires_at: float
    created_at: float
    hits: int = 0

class TTLRUCache:
    """Combined TTL + LRU cache.

    Not thread-safe (assumes single-threaded async usage or external locking).
    """
    def __init__(self, max_entries: int = 256, default_ttl: float = 60.0):
        self.max_entries = max_entries
        self.default_ttl = default_ttl
        self._store: OrderedDict[str, CacheEntry] = OrderedDict()
        self.hits = 0
        self.misses = 0
        self.evictions = 0
        self.expired = 0

    def _purge_expired(self):
        now = time.time()
        to_delete = [k for k, v in self._store.items() if v.expires_at < now]
        for k in to_delete:
            self._store.pop(k, None)
            self.expired += 1

    def _evict_lru(self):
        while len(self._store) > self.max_entries:
            _, _ = self._store.popitem(last=False)
            self.evictions += 1

    def set(self, key: str, value: Any, ttl: Optional[float] = None):
        self._purge_expired()
        ttl = self.default_ttl if ttl is None else ttl
        entry = CacheEntry(value=value, expires_at=time.time() + ttl, created_at=time.time())
        if key in self._store:
            self._store.pop(key, None)
        self._store[key] = entry
        self._store.move_to_end(key, last=True)
        self._evict_lru()

    def get(self, key: str) -> Optional[Any]:
        self._purge_expired()
        entry = self._store.get(key)
        if not entry:
            self.misses += 1
            return None
        if entry.expires_at < time.time():
            self._store.pop(key, None)
            self.expired += 1
            self.misses += 1
            return None
        self.hits += 1
        entry.hits += 1
        self._store.move_to_end(key, last=True)
        return entry.value

    def stats(self) -> Dict[str, Any]:
        self._purge_expired()
        return {
            "size": len(self._store),
            "hits": self.hits,
            "misses": self.misses,
            "evictions": self.evictions,
            "expired": self.expired,
            "max_entries": self.max_entries,
            "default_ttl": self.default_ttl,
        }

    def clear(self):
        self._store.clear()
        self.hits = self.misses = self.evictions = self.expired = 0
