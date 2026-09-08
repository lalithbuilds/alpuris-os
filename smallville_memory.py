import time
import math
import random
from typing import List, Dict, Any, Optional

try:
    from cognitive_core import query_hybrid_llm
except ImportError:
    from ray_agent_world.cognitive_core import query_hybrid_llm


class ConceptNode:
    def __init__(
        self,
        node_id: str,
        node_type: str,
        description: str,
        created_tick: int,
        poignancy: float = 3.0,
        keywords: Optional[List[str]] = None
    ):
        self.node_id = node_id
        self.node_type = node_type
        self.description = description
        self.created_tick = created_tick
        self.last_accessed_tick = created_tick
        self.poignancy = max(1.0, min(10.0, float(poignancy)))
        self.keywords = keywords or []
        self.access_count = 1

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_id": self.node_id,
            "node_type": self.node_type,
            "description": self.description,
            "created_tick": self.created_tick,
            "poignancy": self.poignancy,
            "keywords": self.keywords,
            "access_count": self.access_count
        }


class AssociativeMemoryStream:
    def __init__(self, citizen_id: str, citizen_name: str, reflection_threshold: float = 35.0):
        self.citizen_id = citizen_id
        self.citizen_name = citizen_name
        self.reflection_threshold = reflection_threshold
        self.accumulated_importance = 0.0
        self.node_counter = 0
        self.nodes: List[ConceptNode] = []
        self.reflections: List[Dict[str, Any]] = []

    def _generate_node_id(self) -> str:
        self.node_counter += 1
        return f"{self.citizen_id}_node_{self.node_counter}"

    def add_memory(
        self,
        description: str,
        node_type: str = "event",
        current_tick: int = 0,
        poignancy: Optional[float] = None,
        keywords: Optional[List[str]] = None
    ) -> ConceptNode:
        if poignancy is None:
            desc_lower = description.lower()
            if any(k in desc_lower for k in ["critical", "failure", "alert", "emergency", "voltage", "blackout", "crash"]):
                poignancy = random.uniform(8.0, 10.0)
            elif any(k in desc_lower for k in ["signal", "delay", "ipo", "pitch", "funding", "contract", "bounty", "build"]):
                poignancy = random.uniform(5.5, 7.8)
            elif any(k in desc_lower for k in ["coffee", "dosa", "lunch", "metro", "chai", "drizzle"]):
                poignancy = random.uniform(2.0, 4.0)
            else:
                poignancy = random.uniform(3.0, 5.0)

        node = ConceptNode(
            node_id=self._generate_node_id(),
            node_type=node_type,
            description=description,
            created_tick=current_tick,
            poignancy=poignancy,
            keywords=keywords or []
        )
        self.nodes.append(node)
        self.accumulated_importance += node.poignancy
        return node

    def retrieve(self, query: str, current_tick: int, top_k: int = 4) -> List[ConceptNode]:
        if not self.nodes:
            return []

        query_tokens = set(query.lower().split())
        scored_nodes = []

        for node in self.nodes:
            tick_diff = max(0, current_tick - node.last_accessed_tick)
            recency_score = math.exp(-0.08 * tick_diff)
            importance_score = node.poignancy / 10.0

            node_tokens = set(node.description.lower().split())
            if query_tokens and node_tokens:
                overlap = len(query_tokens & node_tokens)
                relevance_score = overlap / max(1, len(query_tokens))
            else:
                relevance_score = 0.1

            total_score = (recency_score * 0.35) + (importance_score * 0.45) + (relevance_score * 0.20)
            scored_nodes.append((total_score, node))

        scored_nodes.sort(key=lambda x: x[0], reverse=True)
        results = [node for _, node in scored_nodes[:top_k]]
        for n in results:
            n.last_accessed_tick = current_tick
            n.access_count += 1
        return results

    def should_reflect(self) -> bool:
        return self.accumulated_importance >= self.reflection_threshold

    def execute_reflection(self, current_tick: int) -> Optional[Dict[str, Any]]:
        if not self.should_reflect() or len(self.nodes) < 5:
            return None

        self.accumulated_importance = 0.0
        recent_memories = [n.description for n in self.nodes[-10:]]
        mem_text = "\n".join([f"- {m}" for m in recent_memories])

        prompt = (
            f"You are the internal consciousness of {self.citizen_name} in Bengaluru.\n"
            f"Here are your recent observations and experiences:\n{mem_text}\n\n"
            f"Synthesize the single most important high-level insight or long-term plan you draw from these events. "
            f"Respond in 1 clear, reflective sentence in first person."
        )

        try:
            insight = query_hybrid_llm(
                [{"role": "user", "content": prompt}],
                task_type="world_thought",
                timeout=4.0
            )
            insight = insight.strip().replace('"', '')
            if len(insight) > 180:
                insight = insight[:177] + "..."
        except Exception:
            insight = "Observing the city flow, I realize proactive coordination and resilient infra are essential across Bengaluru today."

        reflection_node = self.add_memory(
            description=f"[Reflection] {insight}",
            node_type="thought",
            current_tick=current_tick,
            poignancy=8.8,
            keywords=["reflection", "insight", "goal"]
        )

        reflection_record = {
            "tick": current_tick,
            "citizen_id": self.citizen_id,
            "citizen_name": self.citizen_name,
            "insight": insight,
            "node_id": reflection_node.node_id
        }
        self.reflections.append(reflection_record)
        return reflection_record
