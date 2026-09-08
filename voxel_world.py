"""
Physical Voxel & Spatial Grid World Engine for Bengaluru Living Metropolis
Adapted from Minecraft / Project Sid / Voyager mechanics for embodied world modification.
Enables citizens to place blocks, construct physical infrastructure, repair city assets,
and permanently mutate the spatial environment for all other agents.
"""

import os
import time
import json
import sqlite3
import threading
from typing import Dict, List, Any, Optional, Tuple

DB_PATH = "/Users/lalith/ray_agent_world/world_memory.sqlite"

BLOCK_TYPES = {
    "solar_panel": {"category": "energy", "durability": 100, "color": "#10b981", "cost_inr": 8500},
    "server_rack": {"category": "compute", "durability": 150, "color": "#3b82f6", "cost_inr": 25000},
    "fiber_conduit": {"category": "network", "durability": 80, "color": "#8b5cf6", "cost_inr": 3500},
    "concrete_wall": {"category": "structure", "durability": 300, "color": "#64748b", "cost_inr": 2000},
    "glass_facade": {"category": "architecture", "durability": 50, "color": "#38bdf8", "cost_inr": 5000},
    "metro_track_rail": {"category": "transit", "durability": 250, "color": "#a855f7", "cost_inr": 15000},
    "ev_charging_station": {"category": "mobility", "durability": 120, "color": "#06b6d4", "cost_inr": 12000},
    "filter_coffee_kiosk": {"category": "amenity", "durability": 60, "color": "#d97706", "cost_inr": 7500},
    "road_patch": {"category": "civic", "durability": 200, "color": "#475569", "cost_inr": 4000},
    "voltage_transformer": {"category": "grid", "durability": 180, "color": "#ef4444", "cost_inr": 30000},
    "tree_canopy": {"category": "greenery", "durability": 40, "color": "#22c55e", "cost_inr": 1500}
}

BLUEPRINTS = {
    "quantum_datacenter_pod": [
        (0, 0, "server_rack"), (1, 0, "server_rack"), (0, 1, "fiber_conduit"),
        (1, 1, "solar_panel"), (0, 2, "concrete_wall"), (1, 2, "glass_facade")
    ],
    "rooftop_solar_grid": [
        (0, 0, "solar_panel"), (1, 0, "solar_panel"), (2, 0, "solar_panel"),
        (0, 1, "solar_panel"), (1, 1, "voltage_transformer"), (2, 1, "solar_panel")
    ],
    "metro_flyover_extension": [
        (0, 0, "concrete_wall"), (1, 0, "metro_track_rail"), (2, 0, "metro_track_rail"),
        (3, 0, "concrete_wall")
    ],
    "indiranagar_cafe_pod": [
        (0, 0, "filter_coffee_kiosk"), (1, 0, "tree_canopy"), (0, 1, "glass_facade")
    ],
    "silk_board_congestion_relief": [
        (0, 0, "road_patch"), (1, 0, "road_patch"), (2, 0, "road_patch"),
        (1, 1, "ev_charging_station")
    ]
}


class VoxelWorldGrid:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self.lock = threading.Lock()
        self._init_db()

    def _init_db(self):
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS physical_world_blocks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    zone TEXT NOT NULL,
                    x INTEGER NOT NULL,
                    y INTEGER NOT NULL,
                    z INTEGER DEFAULT 0,
                    block_type TEXT NOT NULL,
                    owner_id TEXT NOT NULL,
                    owner_name TEXT NOT NULL,
                    durability INTEGER DEFAULT 100,
                    created_tick INTEGER NOT NULL,
                    metadata TEXT,
                    UNIQUE(zone, x, y, z)
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS world_construction_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tick INTEGER NOT NULL,
                    citizen_id TEXT NOT NULL,
                    citizen_name TEXT NOT NULL,
                    action_type TEXT NOT NULL,
                    zone TEXT NOT NULL,
                    coords TEXT NOT NULL,
                    details TEXT NOT NULL,
                    timestamp REAL NOT NULL
                )
            """)
            conn.commit()
            conn.close()

    def place_block(
        self,
        citizen_id: str,
        citizen_name: str,
        zone: str,
        x: int,
        y: int,
        block_type: str,
        tick: int,
        z: int = 0,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Places a physical voxel block into the Bengaluru environment."""
        if block_type not in BLOCK_TYPES:
            block_type = "concrete_wall"

        durability = BLOCK_TYPES[block_type]["durability"]
        meta_json = json.dumps(metadata or {})

        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO physical_world_blocks (zone, x, y, z, block_type, owner_id, owner_name, durability, created_tick, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(zone, x, y, z) DO UPDATE SET
                    block_type=excluded.block_type,
                    owner_id=excluded.owner_id,
                    owner_name=excluded.owner_name,
                    durability=excluded.durability,
                    created_tick=excluded.created_tick,
                    metadata=excluded.metadata
            """, (zone, x, y, z, block_type, citizen_id, citizen_name, durability, tick, meta_json))

            cur.execute("""
                INSERT INTO world_construction_logs (tick, citizen_id, citizen_name, action_type, zone, coords, details, timestamp)
                VALUES (?, ?, ?, 'PLACE_BLOCK', ?, ?, ?, ?)
            """, (tick, citizen_id, citizen_name, zone, f"({x},{y},{z})", f"Built {block_type}", time.time()))
            conn.commit()
            conn.close()

        return {
            "status": "placed",
            "zone": zone,
            "x": x, "y": y, "z": z,
            "block_type": block_type,
            "builder": citizen_name
        }

    def construct_blueprint(
        self,
        citizen_id: str,
        citizen_name: str,
        zone: str,
        origin_x: int,
        origin_y: int,
        blueprint_name: str,
        tick: int
    ) -> List[Dict[str, Any]]:
        """Constructs a multi-block architectural blueprint in the zone."""
        if blueprint_name not in BLUEPRINTS:
            return []

        results = []
        for dx, dy, btype in BLUEPRINTS[blueprint_name]:
            res = self.place_block(
                citizen_id=citizen_id,
                citizen_name=citizen_name,
                zone=zone,
                x=origin_x + dx,
                y=origin_y + dy,
                block_type=btype,
                tick=tick,
                z=0,
                metadata={"blueprint": blueprint_name}
            )
            results.append(res)
        return results

    def remove_or_demolish_block(
        self,
        citizen_id: str,
        citizen_name: str,
        zone: str,
        x: int,
        y: int,
        tick: int,
        z: int = 0
    ) -> bool:
        """Demolishes or harvests a block from the environment."""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            cur.execute("DELETE FROM physical_world_blocks WHERE zone=? AND x=? AND y=? AND z=?", (zone, x, y, z))
            affected = cur.rowcount > 0
            if affected:
                cur.execute("""
                    INSERT INTO world_construction_logs (tick, citizen_id, citizen_name, action_type, zone, coords, details, timestamp)
                    VALUES (?, ?, ?, 'DEMOLISH', ?, ?, 'Demolished block', ?)
                """, (tick, citizen_id, citizen_name, zone, f"({x},{y},{z})", time.time()))
            conn.commit()
            conn.close()
        return affected

    def get_zone_blocks(self, zone: str) -> List[Dict[str, Any]]:
        """Returns all persistent physical blocks in a given zone."""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            cur.execute("""
                SELECT x, y, z, block_type, owner_id, owner_name, durability, created_tick, metadata
                FROM physical_world_blocks WHERE zone=?
            """, (zone,))
            rows = cur.fetchall()
            conn.close()

        blocks = []
        for r in rows:
            blocks.append({
                "x": r[0], "y": r[1], "z": r[2],
                "block_type": r[3],
                "color": BLOCK_TYPES.get(r[3], {}).get("color", "#94a3b8"),
                "category": BLOCK_TYPES.get(r[3], {}).get("category", "general"),
                "owner_id": r[4],
                "owner_name": r[5],
                "durability": r[6],
                "created_tick": r[7]
            })
        return blocks

    def get_all_world_stats(self) -> Dict[str, Any]:
        """Returns global construction counts across Bengaluru."""
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*), COUNT(DISTINCT zone), COUNT(DISTINCT owner_id) FROM physical_world_blocks")
            total_blocks, active_zones, active_builders = cur.fetchone()
            
            cur.execute("""
                SELECT block_type, COUNT(*) FROM physical_world_blocks 
                GROUP BY block_type ORDER BY COUNT(*) DESC LIMIT 5
            """)
            top_blocks = {r[0]: r[1] for r in cur.fetchall()}

            cur.execute("""
                SELECT tick, citizen_name, action_type, zone, coords, details, timestamp
                FROM world_construction_logs ORDER BY id DESC LIMIT 10
            """)
            recent_logs = [
                {
                    "tick": r[0], "builder": r[1], "action": r[2],
                    "zone": r[3], "coords": r[4], "details": r[5]
                }
                for r in cur.fetchall()
            ]
            conn.close()

        return {
            "total_constructed_blocks": total_blocks,
            "active_construction_zones": active_zones,
            "active_citizen_builders": active_builders,
            "top_block_types": top_blocks,
            "recent_construction_logs": recent_logs
        }
