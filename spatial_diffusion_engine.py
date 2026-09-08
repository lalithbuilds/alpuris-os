"""
Spatial Proximity Word-of-Mouth Diffusion Engine
Bengaluru Living Metropolis OS
- Simulates viral contagion strictly based on physical co-location and Namma Metro transit links
- Replaces global statistical diffusion with real spatial peer-to-peer transmission
"""

import random
from typing import Dict, Any, List

class SpatialDiffusionEngine:
    def __init__(self):
        self.active_infections: List[Dict[str, Any]] = []
        self.total_transmissions = 0

    def step_spatial_diffusion(self, citizens: Dict[str, Any], tick: int) -> Dict[str, Any]:
        """Simulate word-of-mouth spread among citizens sharing the same 3D sector or transit line."""
        new_transmissions = []
        
        # Group citizens by current zone
        zones: Dict[str, List[Any]] = {}
        for c in citizens.values():
            loc = c.location
            if loc not in zones:
                zones[loc] = []
            zones[loc].append(c)

        # In each zone with > 2 citizens, a conversation can transmit word-of-mouth
        for zone_name, cohort in zones.items():
            if len(cohort) >= 2 and random.random() < 0.45:
                speaker = random.choice(cohort)
                listener = random.choice([c for c in cohort if c.name != speaker.name])

                topics = [
                    ("BLR-TECH-30 Market Rally", "BULLISH_SENTIMENT"),
                    ("Dev Co-Living PG Community Dinner", "HOUSING_LIFESTYLE"),
                    ("Silk Board Gridlock Workaround", "TRANSIT_EFFICIENCY"),
                    ("New AI DevTool Pricing Autopsy", "MARKET_SKEPTICISM"),
                    ("Bull Temple Basavanagudi Morning Darshan", "HERITAGE_CULTURE")
                ]
                topic, sentiment = random.choice(topics)
                self.total_transmissions += 1

                t_event = {
                    "tick": tick,
                    "zone": zone_name,
                    "speaker": speaker.name,
                    "speaker_role": speaker.role,
                    "listener": listener.name,
                    "listener_role": listener.role,
                    "topic": topic,
                    "sentiment": sentiment,
                    "message": f"💬 [{zone_name}] {speaker.name} shared '{topic}' with {listener.name} during transit/break."
                }
                new_transmissions.append(t_event)
                self.active_infections.append(t_event)

        return {
            "total_spatial_hops": self.total_transmissions,
            "recent_transmissions": self.active_infections[-6:]
        }
