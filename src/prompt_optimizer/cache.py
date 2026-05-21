import hashlib
import json
from typing import Optional, Any
import diskcache

from prompt_optimizer.config import CacheConfig

class PromptCache:
    def __init__(self, config: CacheConfig):
        self.enabled = config.enabled
        if self.enabled:
            self.cache = diskcache.Cache(config.path)
        else:
            self.cache = None

    def _generate_key(self, **kwargs: Any) -> str:
        # Sort keys to ensure deterministic serialization
        sorted_items = sorted(kwargs.items())
        key_str = json.dumps(sorted_items, sort_keys=True)
        return hashlib.sha256(key_str.encode("utf-8")).hexdigest()

    def get(self, **kwargs: Any) -> Optional[str]:
        if not self.enabled or self.cache is None:
            return None

        key = self._generate_key(**kwargs)
        return self.cache.get(key)

    def set(self, value: str, **kwargs: Any) -> None:
        if not self.enabled or self.cache is None:
            return

        key = self._generate_key(**kwargs)
        self.cache.set(key, value)

    def close(self):
        if self.cache:
            self.cache.close()
