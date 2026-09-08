"""
Cognitive Core: Stanford Smallville Architecture (Generative Agents)
Enhanced with:
1. Inter-Agent Natural Spoken Dialogue (converse.py)
2. Social Relationship Graph & Mutual Affinity Tracking
3. Circadian World Clock & Daily Phase Schedule
4. Multi-Key OpenRouter + Apple Silicon M4 Qwen2.5:7B Hybrid Inference
"""

import os
import time
import math
import json
import re
import urllib.request
import urllib.error
import random
import hashlib
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field

ENV_PATH = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(ENV_PATH):
    with open(ENV_PATH, "r") as f:
        for line in f:
            if line.strip() and not line.startswith("#") and "=" in line:
                k, v = line.strip().split("=", 1)
                os.environ[k] = v.strip()

# Multi-Tier Provider Registry
KRUTRIM_API_KEY = os.environ.get("KRUTRIM_API_KEY", "")
KRUTRIM_URL = os.environ.get("KRUTRIM_URL", "https://cloud.olakrutrim.com/v1/chat/completions")
WORLD_ARCHITECT_MODEL = os.environ.get("WORLD_ARCHITECT_MODEL", "gpt-oss-120b")

SARVAM_API_KEY = os.environ.get("SARVAM_API_KEY", "")
SARVAM_URL = os.environ.get("SARVAM_URL", "https://api.sarvam.ai/v1/chat/completions")
CITIZEN_DIALOGUE_MODEL = os.environ.get("CITIZEN_DIALOGUE_MODEL", "sarvam-105b-conversations")

LUMINO_AI_API_KEY = os.environ.get("LUMINO_AI_API_KEY", "")
LUMINO_URL = os.environ.get("LUMINO_URL", "https://api.luminoai.co.in/api/v1/chat/completions")
LUMINO_CONCURRENCY_MODEL = os.environ.get("LUMINO_CONCURRENCY_MODEL", "mimo-2-5")

NVIDIA_API_KEY = os.environ.get("NVIDIA_API_KEY", "")
NVIDIA_URL = os.environ.get("NVIDIA_URL", "https://integrate.api.nvidia.com/v1/chat/completions")
GOVERNANCE_MODEL = os.environ.get("GOVERNANCE_MODEL", "openai/gpt-oss-20b")

OMNIROUTE_URL = os.environ.get("OMNIROUTE_URL", "http://localhost:20128/v1/chat/completions")
OMNIROUTE_API_KEY = os.environ.get("OMNIROUTE_API_KEY", "omniroute-master-key")
OMNIROUTE_MODEL = os.environ.get("OMNIROUTE_MODEL", "nvidia/openai/gpt-oss-20b")

OPENROUTER_KEYS = [k.strip() for k in os.environ.get("OPENROUTER_KEYS", "").split(",") if k.strip()]
if not OPENROUTER_KEYS and os.environ.get("OPENROUTER_API_KEY"):
    OPENROUTER_KEYS = [os.environ.get("OPENROUTER_API_KEY")]

OPENROUTER_MODEL = os.environ.get("OPENROUTER_MODEL", "liquid/lfm-2.5-2.6b:free")
LOCAL_LLM_URL = os.environ.get("LOCAL_LLM_URL", "http://localhost:11434/v1/chat/completions")
LOCAL_LLM_MODEL = os.environ.get("LOCAL_LLM_MODEL", "qwen2.5:7b")

KEY_ROTATION_INDEX = 0

class WorldClock:
    def __init__(self, start_hour: int = 9, start_minute: int = 0):
        self.day = 1
        self.hour = start_hour
        self.minute = start_minute

    def advance(self, minutes: int = 15):
        self.minute += minutes
        while self.minute >= 60:
            self.minute -= 60
            self.hour += 1
        if self.hour >= 24:
            self.hour = 0
            self.day += 1

    def set_time(self, hour: int, minute: int = 0, day: Optional[int] = None):
        self.hour = hour % 24
        self.minute = minute % 60
        if day is not None:
            self.day = day

    def get_time_str(self) -> str:
        period = "AM" if self.hour < 12 else "PM"
        h = self.hour % 12
        if h == 0:
            h = 12
        return f"Day {self.day} • {h:02d}:{self.minute:02d} {period}"

    def get_time_of_day_fraction(self) -> float:
        """Returns 0.0 to 1.0 representing progression through 24-hour cycle."""
        return (self.hour * 60 + self.minute) / 1440.0

    def get_circadian_phase_category(self) -> str:
        """Categorical tag for UI, lighting, and citizen state scheduling."""
        if 0 <= self.hour < 4:
            return "MIDNIGHT"
        elif 4 <= self.hour < 7:
            return "EARLY_MORNING"
        elif 7 <= self.hour < 12:
            return "MORNING"
        elif 12 <= self.hour < 16:
            return "AFTERNOON"
        elif 16 <= self.hour < 18:
            return "LATE_AFTERNOON"
        elif 18 <= self.hour < 21:
            return "EVENING"
        else:
            return "NIGHT"

    def get_circadian_phase(self) -> str:
        """Rich human-readable circadian description of Bengaluru life."""
        if 0 <= self.hour < 4:
            return "Midnight Stargazing & Silent Kernel Compile"
        elif 4 <= self.hour < 7:
            return "Early Morning Dawn & Brahmamuhurtha Mist"
        elif 7 <= self.hour < 9:
            return "Sunrise Darshini Commute & Cubbon Park Jog"
        elif 9 <= self.hour < 12:
            return "Morning Standup & Deep Architecture"
        elif 12 <= self.hour < 14:
            return "Midday Cafeteria Lunch & Founder Patios"
        elif 14 <= self.hour < 16:
            return "Afternoon Sprint & Systems Execution"
        elif 16 <= self.hour < 18:
            return "Late Afternoon Petrichor & Code Reviews"
        elif 18 <= self.hour < 21:
            return "Evening Twilight & MG Road Boulevard Stroll"
        elif 21 <= self.hour < 23:
            return "Night Microbreweries & Family Dinners"
        else:
            return "Late Night Hackathons & Ambient City Quiet"

def clean_llm_output(raw: str, max_len: int = 250) -> str:
    if not raw:
        return ""
    if "<think>" in raw and "</think>" in raw:
        raw = raw.split("</think>")[-1].strip()
    raw = re.sub(r'^[0-9\.\-\*\s]+', '', raw).strip(' "\'\n')
    return raw[:max_len]

PROVIDER_FAILURES: Dict[str, int] = {}
PROVIDER_COOLDOWNS: Dict[str, float] = {}

def _check_provider_ready(name: str) -> bool:
    return time.time() >= PROVIDER_COOLDOWNS.get(name, 0.0)

def _note_provider_outcome(name: str, success: bool):
    if success:
        PROVIDER_FAILURES[name] = 0
    else:
        fails = PROVIDER_FAILURES.get(name, 0) + 1
        PROVIDER_FAILURES[name] = fails
        if fails >= 2:
            PROVIDER_COOLDOWNS[name] = time.time() + 30.0

def query_krutrim_single(messages: List[Dict[str, str]], model: str = None, max_tokens: int = 150, timeout: float = 2.5) -> Optional[str]:
    if not KRUTRIM_API_KEY or not _check_provider_ready("krutrim"):
        return None
    target_model = model or WORLD_ARCHITECT_MODEL
    headers = {"Authorization": f"Bearer {KRUTRIM_API_KEY}", "Content-Type": "application/json"}
    payload = {"model": target_model, "messages": messages, "max_tokens": max_tokens, "temperature": 0.7}
    try:
        req = urllib.request.Request(KRUTRIM_URL, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            msg = data.get("choices", [{}])[0].get("message", {})
            content = msg.get("content") or msg.get("reasoning") or ""
            out = clean_llm_output(content)
            _note_provider_outcome("krutrim", True)
            return out
    except Exception:
        _note_provider_outcome("krutrim", False)
        return None

def query_sarvam_single(messages: List[Dict[str, str]], model: str = None, max_tokens: int = 150, timeout: float = 2.5) -> Optional[str]:
    if not SARVAM_API_KEY or not _check_provider_ready("sarvam"):
        return None
    target_model = model or CITIZEN_DIALOGUE_MODEL
    headers = {"api-subscription-key": SARVAM_API_KEY, "Content-Type": "application/json"}
    payload = {"model": target_model, "messages": messages, "max_tokens": max_tokens, "temperature": 0.7}
    try:
        req = urllib.request.Request(SARVAM_URL, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            msg = data.get("choices", [{}])[0].get("message", {})
            content = msg.get("content") or msg.get("reasoning_content") or ""
            out = clean_llm_output(content)
            _note_provider_outcome("sarvam", True)
            return out
    except Exception:
        _note_provider_outcome("sarvam", False)
        return None

def query_lumino_single(messages: List[Dict[str, str]], model: str = None, max_tokens: int = 150, timeout: float = 2.5) -> Optional[str]:
    if not LUMINO_AI_API_KEY or not _check_provider_ready("lumino"):
        return None
    target_model = model or LUMINO_CONCURRENCY_MODEL
    headers = {
        "Authorization": f"Bearer {LUMINO_AI_API_KEY}",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0"
    }
    payload = {"model": target_model, "messages": messages, "max_tokens": max_tokens, "stream": True, "temperature": 0.7}
    try:
        req = urllib.request.Request(LUMINO_URL, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            tokens = []
            for line in resp:
                l = line.decode("utf-8", errors="ignore").strip()
                if l.startswith("data: ") and l != "data: [DONE]":
                    try:
                        chunk = json.loads(l[6:])
                        delta = chunk.get("choices", [{}])[0].get("delta", {}).get("content", "")
                        if delta:
                            tokens.append(delta)
                    except Exception:
                        pass
            out = clean_llm_output("".join(tokens))
            _note_provider_outcome("lumino", True)
            return out
    except Exception:
        _note_provider_outcome("lumino", False)
        return None

def query_nvidia_single(messages: List[Dict[str, str]], model: str = None, max_tokens: int = 150, timeout: float = 2.5) -> Optional[str]:
    if not NVIDIA_API_KEY or not _check_provider_ready("nvidia"):
        return None
    target_model = model or GOVERNANCE_MODEL
    headers = {"Authorization": f"Bearer {NVIDIA_API_KEY}", "Content-Type": "application/json"}
    payload = {"model": target_model, "messages": messages, "max_tokens": max_tokens, "temperature": 0.7}
    try:
        req = urllib.request.Request(NVIDIA_URL, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            msg = data.get("choices", [{}])[0].get("message", {})
            content = msg.get("content") or msg.get("reasoning_content") or ""
            out = clean_llm_output(content)
            _note_provider_outcome("nvidia", True)
            return out
    except Exception:
        _note_provider_outcome("nvidia", False)
        return None

def query_omniroute_single(messages: List[Dict[str, str]], model: str = None, max_tokens: int = 150, timeout: float = 2.0) -> Optional[str]:
    if not _check_provider_ready("omniroute"):
        return None
    target_model = model or OMNIROUTE_MODEL
    headers = {
        "Authorization": f"Bearer {OMNIROUTE_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {"model": target_model, "messages": messages, "max_tokens": max_tokens, "temperature": 0.7}
    try:
        req = urllib.request.Request(OMNIROUTE_URL, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            msg = data.get("choices", [{}])[0].get("message", {})
            content = msg.get("content") or msg.get("reasoning_content") or msg.get("reasoning") or ""
            out = clean_llm_output(content)
            _note_provider_outcome("omniroute", True)
            return out
    except Exception:
        _note_provider_outcome("omniroute", False)
        return None

def query_openrouter_single(key: str, messages: List[Dict[str, str]], model: str = None, max_tokens: int = 150, timeout: float = 2.5) -> Optional[str]:
    if not _check_provider_ready("openrouter"):
        return None
    target_model = model or OPENROUTER_MODEL
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:9090",
        "X-Title": "Ray Living Agent World OS"
    }
    payload = {
        "model": target_model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": 0.7
    }
    try:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=data, headers=headers, method="POST")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            res = json.loads(resp.read().decode("utf-8"))
            raw = res.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
            out = clean_llm_output(raw)
            _note_provider_outcome("openrouter", True)
            return out
    except Exception:
        _note_provider_outcome("openrouter", False)
        return None

def query_local_m4_llm(messages: List[Dict[str, str]], max_tokens: int = 150, timeout: float = 2.0) -> Optional[str]:
    if not _check_provider_ready("local_m4"):
        return None
    payload = {
        "model": LOCAL_LLM_MODEL,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": 0.7
    }
    try:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(LOCAL_LLM_URL, data=data, headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            res = json.loads(resp.read().decode("utf-8"))
            raw = res.get("choices", [{}])[0].get("message", {}).get("content", "").strip()
            out = clean_llm_output(raw)
            _note_provider_outcome("local_m4", True)
            return out
    except Exception:
        _note_provider_outcome("local_m4", False)
        return None

# Global In-Memory Semantic / Hash Response Cache (LRU + TTL)
COGNITIVE_RESPONSE_CACHE: Dict[str, Tuple[float, str]] = {}
CACHE_TTL_SECONDS = 300  # 5 minutes

def get_cached_response(cache_key: str) -> Optional[str]:
    now = time.time()
    if cache_key in COGNITIVE_RESPONSE_CACHE:
        timestamp, response = COGNITIVE_RESPONSE_CACHE[cache_key]
        if now - timestamp < CACHE_TTL_SECONDS:
            return response
        del COGNITIVE_RESPONSE_CACHE[cache_key]
    return None

def set_cached_response(cache_key: str, response: str):
    if len(COGNITIVE_RESPONSE_CACHE) > 2000:
        oldest_keys = sorted(COGNITIVE_RESPONSE_CACHE.keys(), key=lambda k: COGNITIVE_RESPONSE_CACHE[k][0])[:400]
        for k in oldest_keys:
            del COGNITIVE_RESPONSE_CACHE[k]
    COGNITIVE_RESPONSE_CACHE[cache_key] = (time.time(), response)

def query_hybrid_llm(
    messages: List[Dict[str, str]],
    task_type: str = "general",
    persona_seed: int = 0,
    max_tokens: int = 150,
    timeout: float = 2.8,
    **kwargs
) -> str:
    prompt_str = "|".join(m.get("content", "") for m in messages)
    cache_key = hashlib.sha256(f"{task_type}:{prompt_str[:160]}".encode("utf-8")).hexdigest()
    cached = get_cached_response(cache_key)
    if cached:
        return cached

    start_time = time.time()
    deadline = start_time + timeout

    def _rem_timeout() -> float:
        return max(0.4, min(deadline - time.time(), 2.0))

    def _budget_exhausted() -> bool:
        return time.time() >= (deadline - 0.25)

    # Tier 1: Dialogue & Spoken Interactions -> Sarvam 105B Conversations
    if task_type == "dialogue":
        if not _budget_exhausted():
            out = query_sarvam_single(messages, model=CITIZEN_DIALOGUE_MODEL, max_tokens=max_tokens, timeout=_rem_timeout())
            if out and len(out) > 3:
                return out
        if not _budget_exhausted():
            out = query_krutrim_single(messages, model="gemma-4-31b-it", max_tokens=max_tokens, timeout=_rem_timeout())
            if out and len(out) > 3:
                return out
        if not _budget_exhausted():
            out = query_lumino_single(messages, model=LUMINO_CONCURRENCY_MODEL, max_tokens=max_tokens, timeout=_rem_timeout())
            if out and len(out) > 3:
                return out

    # Tier 2: World Architect / Deep Thinking / System 2 Planning -> Krutrim gpt-oss-120b
    elif task_type in ("world_thought", "architect", "thinking"):
        if not _budget_exhausted():
            out = query_krutrim_single(messages, model=WORLD_ARCHITECT_MODEL, max_tokens=max_tokens, timeout=_rem_timeout())
            if out and len(out) > 3:
                return out
        if not _budget_exhausted():
            out = query_sarvam_single(messages, model="sarvam-105b", max_tokens=max_tokens, timeout=_rem_timeout())
            if out and len(out) > 3:
                return out
        if not _budget_exhausted():
            out = query_lumino_single(messages, model="glm-5-3", max_tokens=max_tokens, timeout=_rem_timeout())
            if out and len(out) > 3:
                return out

    # Tier 3: Governance & Civic Ratification -> NVIDIA NIM
    elif task_type == "governance":
        if not _budget_exhausted():
            out = query_nvidia_single(messages, model=GOVERNANCE_MODEL, max_tokens=max_tokens, timeout=_rem_timeout())
            if out and len(out) > 3:
                return out
        if not _budget_exhausted():
            out = query_krutrim_single(messages, model=WORLD_ARCHITECT_MODEL, max_tokens=max_tokens, timeout=_rem_timeout())
            if out and len(out) > 3:
                return out

    # Tier 4: Citizen Action & Deliberate Cognition (General)
    else:
        if not _budget_exhausted():
            out = query_krutrim_single(messages, model="gemma-4-31b-it", max_tokens=max_tokens, timeout=_rem_timeout())
            if out and len(out) > 3:
                return out
        if not _budget_exhausted():
            out = query_lumino_single(messages, model=LUMINO_CONCURRENCY_MODEL, max_tokens=max_tokens, timeout=_rem_timeout())
            if out and len(out) > 3:
                return out
        if not _budget_exhausted():
            out = query_sarvam_single(messages, model=CITIZEN_DIALOGUE_MODEL, max_tokens=max_tokens, timeout=_rem_timeout())
            if out and len(out) > 3:
                return out

    # Tier 5: OmniRoute Gateway
    if not _budget_exhausted():
        omni_out = query_omniroute_single(messages, max_tokens=max_tokens, timeout=_rem_timeout())
        if omni_out and len(omni_out) > 3:
            return omni_out

    # Tier 6: OpenRouter multi-key rotation
    global KEY_ROTATION_INDEX
    if OPENROUTER_KEYS and not _budget_exhausted():
        key = OPENROUTER_KEYS[(KEY_ROTATION_INDEX + persona_seed) % len(OPENROUTER_KEYS)]
        KEY_ROTATION_INDEX = (KEY_ROTATION_INDEX + 1) % len(OPENROUTER_KEYS)
        out = query_openrouter_single(key, messages, max_tokens=max_tokens, timeout=_rem_timeout())
        if out and len(out) > 3:
            return out

    # Tier 7: Apple Silicon M4 Local Model
    if not _budget_exhausted():
        local_out = query_local_m4_llm(messages, max_tokens=max_tokens, timeout=_rem_timeout())
        if local_out and len(local_out) > 3:
            return local_out

    # Fast authentic Bengaluru fallback (Zero Stutter)
    if task_type == "dialogue":
        return "Namaskara! Reviewing system telemetry across Bangalore.\nTelemetry looks locked and stable today."
    elif task_type in ("world_thought", "thinking", "architect"):
        return "Synthesizing city metrics, continuous infrastructure resilience remains the highest operational priority."
    elif task_type == "governance":
        return "Civic proposal ratified under municipal consensus."
    else:
        return "Verifying distributed telemetry and service mesh health"

@dataclass
class MemoryNode:
    id: str
    created_at: float
    last_accessed: float
    content: str
    importance: float
    arousal: float
    node_type: str
    keywords: List[str] = field(default_factory=list)

class MemoryStream:
    def __init__(self, decay_factor: float = 0.995):
        self.nodes: List[MemoryNode] = []
        self.decay_factor = decay_factor
        self.cumulative_importance = 0.0

    def add(self, content: str, importance: float, arousal: float, node_type: str = "observation") -> MemoryNode:
        now = time.time()
        words = [w.lower() for w in content.split() if len(w) > 3]
        node = MemoryNode(
            id=f"mem_{len(self.nodes)+1}_{int(now*1000)%10000}",
            created_at=now,
            last_accessed=now,
            content=content,
            importance=min(1.0, max(0.1, importance)),
            arousal=min(1.0, max(0.0, arousal)),
            node_type=node_type,
            keywords=words
        )
        self.nodes.append(node)
        self.cumulative_importance += node.importance
        return node

    def retrieve(self, query: str, top_k: int = 5) -> List[MemoryNode]:
        if not self.nodes:
            return []
        now = time.time()
        query_words = set(query.lower().split())
        scored: List[tuple[float, MemoryNode]] = []

        for node in self.nodes:
            elapsed_m = (now - node.last_accessed) / 60.0
            recency = math.pow(self.decay_factor, elapsed_m)
            common = len(query_words.intersection(node.keywords))
            relevance = min(1.0, common / (len(query_words) or 1))
            score = 0.5 * recency + 0.3 * node.importance + 0.2 * relevance
            scored.append((score, node))
            node.last_accessed = now

        scored.sort(key=lambda x: x[0], reverse=True)
        return [item[1] for item in scored[:top_k]]

    def should_reflect(self, threshold: float = 4.0) -> bool:
        return self.cumulative_importance >= threshold

    def reflect(self) -> Optional[MemoryNode]:
        if not self.should_reflect() or len(self.nodes) < 3:
            return None
        self.cumulative_importance = 0.0
        recent = self.nodes[-5:]
        summary_content = f"Synthesized reflection on: {'; '.join(m.content[:40] for m in recent)}"
        mean_arousal = sum(m.arousal for m in recent) / len(recent)
        return self.add(summary_content, importance=0.85, arousal=mean_arousal, node_type="reflection")

class Persona:
    def __init__(self, id: str, name: str, role: str, starting_location: str = "Manyata_Tech_Park", department: str = "Core Architecture"):
        self.id = id
        self.name = name
        self.role = role
        self.department = department
        self.location = starting_location
        self.home_zone = "HSR_Layout_Residences"
        self.workplace = starting_location
        self.memory = MemoryStream()
        self.current_arousal = 0.25
        self.status = "ACTIVE"
        self.current_task = f"Active in {starting_location}"
        self.computer_logs: List[str] = []
        self.onsets: List[float] = []
        self.is_active_shift = True
        self.last_action = "Initialized in Bengaluru"
        
        # Bengaluru Living Economy
        self.wallet_inr = 25000.0  # ₹25,000 initial bank balance
        self.energy = 100.0        # 0 - 100% stamina
        
        # Social Graph & Rumor Network
        self.relationships: Dict[str, Dict[str, Any]] = {}
        self.known_rumors: List[str] = []
        
        # Hierarchical Goal Tree (DAG)
        self.current_goal = f"Execute {role} responsibilities in Bengaluru"
        self.subtasks: List[str] = [
            f"Transit from {self.home_zone} via Namma Metro",
            f"Review daily tasks at {self.workplace}",
            "Coordinate with cross-team colleagues",
            "Evening debrief and relaxation"
        ]
        self.speech_bubble: Optional[Dict[str, Any]] = None

    def can_afford(self, amount: float) -> bool:
        return self.wallet_inr >= amount

    def spend_inr(self, amount: float, reason: str) -> bool:
        if self.wallet_inr >= amount:
            self.wallet_inr = round(self.wallet_inr - amount, 2)
            self.memory.add(f"Spent ₹{amount} on {reason}. Balance: ₹{int(self.wallet_inr)}", importance=0.4, arousal=0.1)
            return True
        else:
            self.memory.add(f"Insufficient funds for {reason} (Required: ₹{amount}, Balance: ₹{int(self.wallet_inr)})", importance=0.3, arousal=0.3)
            return False

    def earn_inr(self, amount: float, reason: str):
        self.wallet_inr += amount
        self.memory.add(f"Earned ₹{amount} bounty for {reason}. Balance: ₹{int(self.wallet_inr)}", importance=0.8, arousal=0.2)

    def adjust_energy(self, delta: float):
        self.energy = min(100.0, max(10.0, self.energy + delta))

    def perceive(self, event_text: str, stress_impact: float = 0.0):
        self.current_arousal = min(1.0, max(0.1, self.current_arousal + stress_impact))
        self.memory.add(event_text, importance=0.5 + abs(stress_impact) * 0.5, arousal=self.current_arousal)
        if self.memory.should_reflect():
            reflection = self.memory.reflect()
            if reflection:
                self.computer_logs.append(f"[Cognition] {reflection.content}")

    def decide_dual_speed_action(self, world_context: str, is_novel: bool = False, seed: int = 0) -> str:
        """
        PIANO Dual-Speed Engine:
        - System 1 (Reflex): Instant (<1ms) situational micro-actions for routine ticks.
        - System 2 (Deliberate LLM): Triggered for novel events, location changes, or critical decisions.
        """
        # System 1 Fast Reflex Lookup
        if not is_novel and random.random() < 0.65:
            reflexes = {
                "Kempegowda_Airport_BLR": [
                    "Reviewing international cloud infrastructure specs at BLR terminal",
                    "Connecting to airport Wi-Fi and syncing distributed commits",
                    "Welcoming visiting tech delegation at Arrival Gate 4",
                    "Checking flight telematics and radar weather displays"
                ],
                "Manyata_Tech_Park": [
                    "Monitoring high-density cloud servers at Manyata",
                    "Benchmarking distributed ZeroMQ IPC throughput",
                    "Reviewing pull request telemetry on dual monitors",
                    "Debugging memory-mapped shm ring buffer allocations"
                ],
                "IISc_Research_Campus": [
                    "Synthesizing topological quantum gate simulations",
                    "Reading preprint paper on neuromorphic spiking networks",
                    "Calibrating cryogenic dilution refrigerator sensors",
                    "Discussing protein folding embeddings at IISc canteen"
                ],
                "Whitefield_ITPB": [
                    "Inspecting enterprise server rack arrays at ITPB",
                    "Testing distributed consensus under network partition",
                    "Coordinating with international offshore engineering squads",
                    "Auditing enterprise cloud security boundaries"
                ],
                "Bagmane_Tech_Park": [
                    "Developing low-latency microservices at Bagmane",
                    "Benchmarking Rust data pipeline on Apple Silicon",
                    "Refactoring GraphQL schema for mobile clients",
                    "Pair programming on distributed cache invalidation"
                ],
                "Indiranagar_100ft_Startups": [
                    "Refactoring React Canvas widgets at Indiranagar incubator",
                    "Prototyping Glassmorphism dashboard in Tailwind",
                    "Pair programming on autonomous compiler syntax trees",
                    "Pitching seed-stage AI agent roadmap to visiting angel"
                ],
                "Vidhana_Soudha_Capitol": [
                    "Reviewing municipal tech policy at Vidhana Soudha",
                    "Briefing City Mayor Tara Sen on infrastructure metrics",
                    "Drafting data governance guidelines for Bengaluru OS",
                    "Tabulating municipal council votes on city ordinances"
                ],
                "Cubbon_Park_Canopy": [
                    "Taking a quiet walk under bamboo groves in Cubbon Park",
                    "Synthesizing cognitive reflections and reducing stress",
                    "Mindfulness break near the State Central Library",
                    "Reading architecture notes amidst morning bird calls"
                ],
                "Church_Street_Cafes": [
                    "Reading latest ArXiv multi-agent paper over filter coffee",
                    "Browsing technical books at Blossom Book House",
                    "Casual hallway discussion outside Church Street cafe",
                    "Drafting tech column for The Bengaluru Chronicle"
                ],
                "UB_City_Luxury_Towers": [
                    "Analyzing startup term sheets on UB City 14th floor",
                    "Reviewing venture fund liquidity and seed valuations",
                    "Board meeting on scaling enterprise AI agent platforms",
                    "Monitoring BSE and BLR-TECH-30 index fluctuations"
                ],
                "Majestic_Metro_Interchange": [
                    "Swiping Namma Metro smartcard at Majestic gates",
                    "Transferring between Purple Line and Green Line platforms",
                    "Checking train arrival display board at Majestic",
                    "Observing inter-city bus departures at KSRTC terminal"
                ],
                "Gandhi_Bazaar_Heritage": [
                    "Enjoying crispy benne dosa and filter coffee at Vidyarthi Bhavan",
                    "Picking up fresh jasmine and South Indian spices",
                    "Catching up with neighborhood elders on Gandhi Bazaar road",
                    "Soaking in historic South Bengaluru cultural warmth"
                ],
                "Nexus_Koramangala_Mall": [
                    "Grabbing lunch at Koramangala food court with colleagues",
                    "Observing consumer tech and retail analytics displays",
                    "Short afternoon coffee break at Koramangala cafe",
                    "Testing point-of-sale contactless payment SDK"
                ],
                "Silk_Board_Junction": [
                    "Waiting at Silk Board flyover signal during peak transit",
                    "Observing vehicle telematics and bus flow at Silk Board",
                    "Checking real-time GPS traffic heatmaps on mobile",
                    "Navigating electric auto through Outer Ring Road traffic"
                ],
                "HSR_Layout_Residences": [
                    "Evening debrief at HSR Layout co-living apartment",
                    "Recharging battery and syncing daily memory logs",
                    "Planning tomorrow's transit route and priority backlog",
                    "Cooking quick meal while streaming tech podcast"
                ],
                "Electronic_City_Phase_1": [
                    "Inspecting enterprise hardware racks and switches",
                    "Flashing firmware and validating embedded edge telemetry",
                    "Running network packet inspection on edge gateways",
                    "Testing smart grid energy controllers on campus"
                ]
            }
            options = reflexes.get(self.location)
            if not options:
                # Fallback fuzzy matching
                for k, v in reflexes.items():
                    if k.split("_")[0] in self.location or self.location.split("_")[0] in k:
                        options = v
                        break
            options = options or ["Analyzing operational telemetry in Bengaluru"]
            decision = random.choice(options)
            self.last_action = decision
            self.set_speech_bubble(decision[:40])
            self.adjust_energy(-0.5)
            return f"[Reflex] {decision}"

        # System 2 Deliberate LLM Cognition
        prompt = (
            f"You are {self.name}, an autonomous citizen of Bengaluru working as '{self.role}' in '{self.department}', currently at '{self.location}'. "
            f"Context: {world_context}. Energy: {int(self.energy)}%, Wallet: ₹{int(self.wallet_inr)}. "
            f"State 1 realistic, authentic action (under 12 words) you execute right now in Bengaluru."
        )
        decision = query_hybrid_llm([{"role": "user", "content": prompt}], task_type="action", persona_seed=seed, max_tokens=35)
        decision = decision.strip(' ."\n')
        self.last_action = decision
        self.set_speech_bubble(decision[:40])
        self.adjust_energy(-2.0)
        return f"[LLM] {decision}"

    def set_speech_bubble(self, text: str):
        self.speech_bubble = {
            "text": text,
            "timestamp": time.time()
        }

    def converse_with(self, partner: 'Persona', zone: str, current_context: str) -> Optional[Dict[str, Any]]:
        """Stanford Smallville Spoken Conversation + Bengaluru Rumor Diffusion Network."""
        prompt = (
            f"Simulate a natural, realistic spoken conversation between two colleagues meeting in Bengaluru:\n"
            f"Citizen 1: {self.name} ({self.role}, {self.department})\n"
            f"Citizen 2: {partner.name} ({partner.role}, {partner.department})\n"
            f"Location: {zone} in Bengaluru. Context: {current_context}\n"
            f"Rules: Speak naturally like real Bengaluru tech colleagues (casual, technical, colloquial).\n"
            f"Exactly 2 lines total:\n"
            f"{self.name}: [spoken line]\n"
            f"{partner.name}: [spoken line]"
        )
        dialogue_raw = query_hybrid_llm([{"role": "user", "content": prompt}], task_type="dialogue", max_tokens=120)

        p1_said = None
        p2_said = None

        for line in dialogue_raw.strip().splitlines():
            line = line.strip()
            if self.name in line and ":" in line:
                p1_said = line.split(":", 1)[1].strip(' "\'')
            elif partner.name in line and ":" in line:
                p2_said = line.split(":", 1)[1].strip(' "\'')

        if not p1_said:
            p1_said = f"Hey {partner.name.split()[0]}, how's the traffic getting to {zone.replace('_', ' ')} today?"
        if not p2_said:
            p2_said = f"Namma Metro saved me, {self.name.split()[0]}. Silk Board was totally jammed as usual!"

        self.set_speech_bubble(p1_said[:40])
        partner.set_speech_bubble(p2_said[:40])

        self.perceive(f"Met {partner.name} at {zone}: '{p1_said}' -> '{p2_said}'", stress_impact=-0.04)
        partner.perceive(f"Met {self.name} at {zone}: '{p1_said}' -> '{p2_said}'", stress_impact=-0.04)

        # Rumor Diffusion: Share rumors between citizens
        if self.known_rumors and not partner.known_rumors:
            partner.known_rumors.append(self.known_rumors[-1])
            partner.perceive(f"Rumor from {self.name}: {self.known_rumors[-1]}", stress_impact=0.1)
        elif partner.known_rumors and not self.known_rumors:
            self.known_rumors.append(partner.known_rumors[-1])
            self.perceive(f"Rumor from {partner.name}: {partner.known_rumors[-1]}", stress_impact=0.1)

        # Social Affinity
        r1 = self.relationships.setdefault(partner.id, {"affinity": 0.5, "encounters": 0, "partner_name": partner.name})
        r1["encounters"] += 1
        r1["affinity"] = min(1.0, r1["affinity"] + 0.05)
        r1["last_talk"] = p1_said

        r2 = partner.relationships.setdefault(self.id, {"affinity": 0.5, "encounters": 0, "partner_name": self.name})
        r2["encounters"] += 1
        r2["affinity"] = min(1.0, r2["affinity"] + 0.05)
        r2["last_talk"] = p2_said

        return {
            "speaker_1": self.name,
            "speaker_2": partner.name,
            "dept_1": self.department,
            "dept_2": partner.department,
            "zone": zone,
            "turn_1": p1_said,
            "turn_2": p2_said,
            "affinity": round(r1["affinity"], 2)
        }

    def chat_with_creator(self, creator_message: str) -> str:
        prompt = (
            f"You are {self.name}, an autonomous citizen of Bengaluru ({self.role} in {self.department}), at {self.location}. "
            f"City Governor Lalith instructed you: '{creator_message}'. "
            f"Respond directly to Lalith in 1-2 concise, respectful, authentic sentences."
        )
        reply = query_hybrid_llm([{"role": "user", "content": prompt}], task_type="creator", max_tokens=90)
        self.perceive(f"Governor Lalith instructed: '{creator_message}'. Replied: '{reply}'", stress_impact=0.15)
        self.set_speech_bubble(f"To Lalith: {reply[:35]}")
        return reply

    def log_computer_action(self, action_msg: str):
        self.last_action = action_msg
        self.computer_logs.append(f"[{time.strftime('%H:%M:%S')}] {action_msg}")
        if len(self.computer_logs) > 20:
            self.computer_logs.pop(0)
