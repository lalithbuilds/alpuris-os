"""
Citizen Vector Brain: Semantic Memory Store
Bengaluru Living Metropolis OS
- Provides localized vector embeddings for citizen autobiographical memory recall
- Indexes conversations, commitments, financial autopsies, and peer impressions
"""

import math
import hashlib
import time
from typing import Dict, Any, List, Tuple

class CitizenVectorBrain:
    def __init__(self, vector_dim: int = 32):
        self.vector_dim = vector_dim
        # citizen_id -> list of (vector, memory_dict)
        self.citizen_memories: Dict[str, List[Tuple[List[float], Dict[str, Any]]]] = {}

    def _pseudo_embed(self, text: str) -> List[float]:
        """Deterministic lightweight embedding vector using SHA-256 seed projection."""
        h = hashlib.sha256(text.lower().encode()).digest()
        vec = []
        for i in range(self.vector_dim):
            byte_val = h[i % len(h)]
            # Map byte to [-1.0, 1.0]
            val = (byte_val / 127.5) - 1.0
            vec.append(val)
        # Normalize
        norm = math.sqrt(sum(x * x for x in vec)) or 1.0
        return [x / norm for x in vec]

    def store_memory(self, citizen_id: str, citizen_name: str, memory_text: str, context_type: str, tick: int):
        vec = self._pseudo_embed(memory_text)
        record = {
            "citizen_id": citizen_id,
            "citizen_name": citizen_name,
            "text": memory_text,
            "type": context_type,
            "tick": tick,
            "timestamp": time.time()
        }
        if citizen_id not in self.citizen_memories:
            self.citizen_memories[citizen_id] = []
        self.citizen_memories[citizen_id].append((vec, record))

    def recall_semantic(self, citizen_id: str, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        if citizen_id not in self.citizen_memories:
            return []
        q_vec = self._pseudo_embed(query)
        scored = []
        for vec, rec in self.citizen_memories[citizen_id]:
            sim = sum(a * b for a, b in zip(q_vec, vec))
            scored.append((sim, rec))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [rec for _, rec in scored[:top_k]]

    def get_total_indexed_memories(self) -> int:
        return sum(len(mems) for mems in self.citizen_memories.values())
