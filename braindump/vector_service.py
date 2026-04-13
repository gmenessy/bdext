# 🧠 BrainDump (v3) - Vector-Lite Service (Deterministic)
import json
import os
import math
import hashlib
from typing import List, Dict, Any, Tuple

class VectorService:
    """
    Provides semantic search capabilities using a local vector index.
    Deterministic hashing (MD5) for cross-restart persistence.
    """
    def __init__(self, index_path: str = "vector/index.json"):
        self.index_path = index_path
        self.index: Dict[str, List[float]] = {}
        self._load()

    def _load(self):
        if os.path.exists(self.index_path):
            with open(self.index_path, "r") as f:
                self.index = json.load(f)

    def _save(self):
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        with open(self.index_path, "w") as f:
            json.dump(self.index, f)

    def _get_embedding(self, text: str) -> List[float]:
        """
        Generates a deterministic semantic vector based on character n-grams.
        """
        text = text.lower()
        ngrams = [text[i:i+3] for i in range(len(text)-2)]
        
        vec = [0.0] * 128
        for gram in ngrams:
            # Deterministic hash (MD5)
            h = int(hashlib.md5(gram.encode()).hexdigest(), 16)
            idx = h % 128
            vec[idx] += 1.0
        
        # Normalize
        norm = math.sqrt(sum(x*x for x in vec)) or 1.0
        return [x/norm for x in vec]

    def index_content(self, path: str, text: str):
        """Indexes a VFS path with its semantic embedding."""
        embedding = self._get_embedding(text)
        self.index[path] = embedding
        self._save()

    def search(self, query: str, limit: int = 5) -> List[Tuple[str, float]]:
        """Finds the most semantically similar VFS paths."""
        query_vec = self._get_embedding(query)
        scores = []
        
        for path, doc_vec in self.index.items():
            # Cosine Similarity
            dot_product = sum(a*b for a, b in zip(query_vec, doc_vec))
            scores.append((path, dot_product))
        
        # Sort by score descending
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:limit]
