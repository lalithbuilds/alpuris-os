"""
Project Sid Persistent Social Graph & Decentralized P2P Contract Market
Adapted from Project Sid (Altera) multi-agent civilization dynamics.
Tracks mutable inter-agent trust, historical favors/betrayals, and bilateral bounties.
"""

import time
import sqlite3
import threading
from typing import Dict, List, Any, Optional

DB_PATH = "/Users/lalith/ray_agent_world/world_memory.sqlite"

class SocialGraph:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self.lock = threading.Lock()
        self._init_db()

    def _init_db(self):
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS social_relationships (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    citizen_a TEXT NOT NULL,
                    citizen_b TEXT NOT NULL,
                    trust REAL DEFAULT 0.5,           -- -1.0 (betrayal/hostile) to +1.0 (deep alliance)
                    familiarity INTEGER DEFAULT 10,   -- 0 to 100
                    status TEXT DEFAULT 'collaborator',-- ally, collaborator, neutral, rival
                    shared_interactions INTEGER DEFAULT 1,
                    last_interaction_tick INTEGER NOT NULL,
                    notes TEXT,
                    UNIQUE(citizen_a, citizen_b)
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS p2p_bounties (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    creator_id TEXT NOT NULL,
                    creator_name TEXT NOT NULL,
                    title TEXT NOT NULL,
                    reward_inr REAL NOT NULL,
                    category TEXT NOT NULL,
                    target_zone TEXT NOT NULL,
                    status TEXT DEFAULT 'OPEN',       -- OPEN, CLAIMED, COMPLETED
                    claimant_id TEXT,
                    claimant_name TEXT,
                    created_tick INTEGER NOT NULL,
                    completed_tick INTEGER
                )
            """)
            conn.commit()
            conn.close()

    def record_interaction(
        self,
        citizen_a: str,
        citizen_b: str,
        tick: int,
        trust_delta: float = 0.05,
        familiarity_delta: int = 5,
        notes: str = ""
    ):
        """Updates bilateral relational edge between two citizens."""
        c1, c2 = sorted([citizen_a, citizen_b])
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            cur.execute("SELECT trust, familiarity, shared_interactions FROM social_relationships WHERE citizen_a=? AND citizen_b=?", (c1, c2))
            row = cur.fetchone()
            if row:
                new_trust = max(-1.0, min(1.0, row[0] + trust_delta))
                new_fam = min(100, row[1] + familiarity_delta)
                new_interactions = row[2] + 1
                status = "ally" if new_trust > 0.65 else ("rival" if new_trust < 0.1 else "collaborator")
                cur.execute("""
                    UPDATE social_relationships 
                    SET trust=?, familiarity=?, status=?, shared_interactions=?, last_interaction_tick=?, notes=?
                    WHERE citizen_a=? AND citizen_b=?
                """, (new_trust, new_fam, status, new_interactions, tick, notes, c1, c2))
            else:
                initial_trust = max(-1.0, min(1.0, 0.5 + trust_delta))
                cur.execute("""
                    INSERT INTO social_relationships (citizen_a, citizen_b, trust, familiarity, status, shared_interactions, last_interaction_tick, notes)
                    VALUES (?, ?, ?, ?, 'collaborator', 1, ?, ?)
                """, (c1, c2, initial_trust, 15, tick, notes))
            conn.commit()
            conn.close()

    def get_citizen_allies_and_rivals(self, citizen_id: str) -> Dict[str, Any]:
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            cur.execute("""
                SELECT CASE WHEN citizen_a=? THEN citizen_b ELSE citizen_a END AS peer,
                       trust, familiarity, status
                FROM social_relationships
                WHERE (citizen_a=? OR citizen_b=?) AND shared_interactions > 1
                ORDER BY trust DESC LIMIT 6
            """, (citizen_id, citizen_id, citizen_id))
            rows = cur.fetchall()
            conn.close()
        return [{"peer": r[0], "trust": round(r[1], 2), "familiarity": r[2], "status": r[3]} for r in rows]

    def get_top_social_bonds(self) -> List[Dict[str, Any]]:
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            cur.execute("""
                SELECT citizen_a, citizen_b, trust, familiarity, status, shared_interactions
                FROM social_relationships ORDER BY shared_interactions DESC LIMIT 10
            """)
            rows = cur.fetchall()
            conn.close()
        return [
            {
                "citizen_a": r[0], "citizen_b": r[1],
                "trust": round(r[2], 2), "familiarity": r[3],
                "status": r[4], "interactions": r[5]
            }
            for r in rows
        ]


class P2PContractMarket:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self.lock = threading.Lock()

    def post_bounty(
        self,
        creator_id: str,
        creator_name: str,
        title: str,
        reward_inr: float,
        category: str,
        target_zone: str,
        tick: int
    ) -> Dict[str, Any]:
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO p2p_bounties (creator_id, creator_name, title, reward_inr, category, target_zone, status, created_tick)
                VALUES (?, ?, ?, ?, ?, ?, 'OPEN', ?)
            """, (creator_id, creator_name, title, reward_inr, category, target_zone, tick))
            b_id = cur.lastrowid
            conn.commit()
            conn.close()
        return {"bounty_id": b_id, "title": title, "reward_inr": reward_inr, "status": "OPEN"}

    def claim_and_complete_bounty(
        self,
        bounty_id: int,
        worker_id: str,
        worker_name: str,
        tick: int
    ) -> Optional[Dict[str, Any]]:
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            cur.execute("SELECT creator_id, reward_inr, title FROM p2p_bounties WHERE id=? AND status='OPEN'", (bounty_id,))
            row = cur.fetchone()
            if not row:
                conn.close()
                return None
            creator_id, reward, title = row
            cur.execute("""
                UPDATE p2p_bounties
                SET status='COMPLETED', claimant_id=?, claimant_name=?, completed_tick=?
                WHERE id=?
            """, (worker_id, worker_name, tick, bounty_id))
            conn.commit()
            conn.close()
        return {
            "bounty_id": bounty_id,
            "creator_id": creator_id,
            "worker_id": worker_id,
            "worker_name": worker_name,
            "reward_inr": reward,
            "title": title
        }

    def get_open_bounties(self) -> List[Dict[str, Any]]:
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            cur.execute("""
                SELECT id, creator_name, title, reward_inr, category, target_zone, created_tick
                FROM p2p_bounties WHERE status='OPEN' ORDER BY id DESC LIMIT 8
            """)
            rows = cur.fetchall()
            conn.close()
        return [
            {
                "id": r[0], "creator": r[1], "title": r[2],
                "reward_inr": r[3], "category": r[4], "zone": r[5], "tick": r[6]
            }
            for r in rows
        ]

    def get_recent_completed_contracts(self) -> List[Dict[str, Any]]:
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            cur.execute("""
                SELECT id, creator_name, claimant_name, title, reward_inr, completed_tick
                FROM p2p_bounties WHERE status='COMPLETED' ORDER BY id DESC LIMIT 6
            """)
            rows = cur.fetchall()
            conn.close()
        return [
            {
                "id": r[0], "creator": r[1], "claimant": r[2],
                "title": r[3], "reward_inr": r[4], "tick": r[5]
            }
            for r in rows
        ]
