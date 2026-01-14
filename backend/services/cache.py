import time
import json
import hashlib
from typing import List, Optional, Dict, Any, Tuple
from collections import OrderedDict
from backend.config import Config

class CacheEntry:
    def __init__(self, value: Any, expires_at: float):
        self.value = value
        self.expires_at = expires_at

class ChatCache:
    def __init__(self):
        self.max_items = Config.CACHE_MAX_ITEMS
        self.ttl = Config.CACHE_TTL_SECONDS
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.hits = 0
        self.misses = 0

    def _generate_key(self, question: str, source_ids: List[str]) -> str:
        """
        Generates a cache key based on inputs and configuration version.
        """
        # 1. Normalize question
        norm_q = question.strip().lower()
        
        # 2. Normalize Source IDs
        norm_sources = ",".join(sorted(source_ids)) if source_ids else "all"
        
        # 3. Config Dependencies (if these change, cache should be invalid)
        config_sig = f"{Config.RETRIEVAL_TOP_K}:{Config.RERANK_ENABLED}:{Config.RERANK_TOP_N}:{Config.INDEX_VERSION}"
        
        raw_key = f"{norm_q}|{norm_sources}|{config_sig}"
        return hashlib.md5(raw_key.encode()).hexdigest()

    def get(self, question: str, source_ids: List[str] = None) -> Optional[Any]:
        if not Config.CACHE_ENABLED:
            return None
            
        key = self._generate_key(question, source_ids or [])
        
        if key not in self._cache:
            self.misses += 1
            return None
            
        entry = self._cache[key]
        
        # Check TTL
        if time.time() > entry.expires_at:
            del self._cache[key]
            self.misses += 1
            return None
            
        # Move to end (LRU)
        self._cache.move_to_end(key)
        self.hits += 1
        return entry.value

    def set(self, question: str, value: Any, source_ids: List[str] = None):
        if not Config.CACHE_ENABLED:
            return

        key = self._generate_key(question, source_ids or [])
        
        # Evict if full
        if len(self._cache) >= self.max_items:
            # OrderedDict pops from 'last=False' for FIFO behaviour if we append to end?
            # Creating LRU: move_to_end on access. So least recently used is at the beginning.
            self._cache.popitem(last=False)
            
        expires_at = time.time() + self.ttl
        self._cache[key] = CacheEntry(value, expires_at)

# Global Instance
chat_cache = ChatCache()
