"""
Bengaluru TV Broadcast Network
Simulates 3 Authentically Programmed 24/7 Live Television Channels:
1. 📺 BLR24 NEWS — Prime Karnataka, Vidhana Soudha, Silk Board Traffic, Bangalore Weather & Civic Alerts
2. 📈 CNBC-BLR TECH & MONEY — Dalal Street, BLR-TECH-30, Startup Valuation, Focus Group Product Autopsies
3. 🌐 METRO GLOBAL & AI PULSE — Silicon Plateau AI Research, Hacker News Tech, Kernel Architecture
"""

import time
import random
from typing import Dict, List, Any, Optional

class BengaluruTVBroadcastNetwork:
    def __init__(self):
        self.channels = {
            "BLR24_NEWS": {
                "id": "BLR24_NEWS",
                "name": "BLR24 NEWS",
                "tagline": "Karnataka's 24/7 Prime News & Civic Heartbeat",
                "anchor": "Rajeshwari Gowda (Senior Prime Time Anchor)",
                "location": "MG Road Broadcast Center, Studio A",
                "badge_color": "#ef4444",
                "current_show": "Namma Bengaluru Super Prime",
                "studio_dialogue": "Good evening Bengaluru. We are tracking high density vehicular buildup along Silk Board Junction as the evening commute peaks. Namma Metro reports record passenger footfalls on the Purple Line.",
                "breaking_ticker": [
                    "BREAKING: Silk Board junction bottleneck operating at 74% congestion; traffic police recommend Outer Ring Road underpass",
                    "NAMMA METRO: Yellow Line automated driverless trainsets clear final trial phase at Bommasandra depot",
                    "CIVIC UPDATE: Cauvery Stage V water distribution pipeline operational across 110 peripheral city wards",
                    "WEATHER DESK: Cool evening petrichor breeze settling over Cubbon Park; overnight temperatures forecast to dip to 18°C"
                ],
                "reporters": ["Chethan Murthy (Silk Board Overpass)", "Sowmya Rao (Vidhana Soudha)"]
            },
            "CNBC_BLR_TECH": {
                "id": "CNBC_BLR_TECH",
                "name": "CNBC-BLR TECH & MONEY",
                "tagline": "Silicon Plateau Markets, Venture Capital & Startup Autopsies",
                "anchor": "Vikram Singhania (Chief Markets Editor)",
                "location": "Indiranagar 100ft Road Studios",
                "badge_color": "#10b981",
                "current_show": "The Koramangala Pitch & Term Sheet",
                "studio_dialogue": "Welcome back to Tech & Money. Markets holding steady with BLR-TECH-30 up 1.2%. Founders across HSR Layout are reassessing burn rates following rigorous synthetic consumer focus group audits.",
                "breaking_ticker": [
                    "MARKETS LIVE: BLR-TECH-30 index consolidates at 26,980 with strong buying in cloud infrastructure and eBPF observability",
                    "STARTUP AUTOPSY: Product 'DevPulse' faces 78% rejection in synthetic focus groups due to aggressive ₹2,499 pricing suicide",
                    "VENTURE PULSE: Peak XV and Accel partner huddle in Koramangala reviewing seed rounds with strict path-to-profitability mandates",
                    "FOREX: USD/INR trading at ₹86.85; Indian tech exporters register steady operating margin expansion"
                ],
                "reporters": ["Ananya Roy (Dalal Street / UB City)", "Rohan Shenoy (Indiranagar Startups)"]
            },
            "METRO_AI_PULSE": {
                "id": "METRO_AI_PULSE",
                "name": "METRO GLOBAL & AI PULSE",
                "tagline": "Frontier Systems, Open-Source Kernels & Global Tech Dispatches",
                "anchor": "Dr. Arjun Somayaji (Chief Technology Correspondent)",
                "location": "Electronic City Innovation Labs",
                "badge_color": "#8b5cf6",
                "current_show": "The Kernel & Singularity Hour",
                "studio_dialogue": "We are monitoring rapid developments in shared-memory POSIX CRDT architectures. The shift from disk-bound databases to sub-microsecond in-memory arenas is revolutionizing real-time agent metropolis engineering.",
                "breaking_ticker": [
                    "AI ARCHITECTURE: Multi-agent synthetic focus group simulations replace legacy polling across consumer software firms",
                    "KERNEL DISPATCH: POSIX shared memory with Cap'n Proto zero-copy serialization hits 100k ops/sec in local benchmarks",
                    "OPEN SOURCE: Linux foundation highlights Bengaluru developer community as top contributor to cloud-native kernel modules",
                    "GLOBAL TECH: Real-time telemetry feeds bridging real-world Open-Meteo weather with virtual 3D voxel skylines"
                ],
                "reporters": ["Maya Iyer (Manyata Tech Park Labs)", "David Chen (Global Wire)"]
            }
        }
        self.active_channel = "BLR24_NEWS"

    def update_broadcast(
        self,
        world_time: str,
        circadian_phase: str,
        weather: Dict[str, Any],
        silk_congestion: int,
        stocks: List[Dict[str, Any]],
        recent_fg_audit: Optional[Dict[str, Any]] = None,
        real_intel: Optional[Dict[str, Any]] = None
    ):
        # 1. Update BLR24 NEWS
        temp_str = weather.get("temp", "23°C")
        cond_str = weather.get("condition", "Pleasant")
        b24 = self.channels["BLR24_NEWS"]
        
        b24_tickers = [
            f"CITY WEATHER: {temp_str} • {cond_str} across all 16 metropolis sectors",
            f"TRAFFIC MONITOR: Silk Board junction at {silk_congestion}% gridlock; Namma Metro Green/Purple lines on schedule",
            f"METROPOLIS CLOCK: {world_time} — {circadian_phase}",
            "BBMP ALERT: Urban tree canopy preservation active across Cubbon Park and Sankey Tank corridors"
        ]
        if real_intel and "india_civic_news" in real_intel:
            for item in real_intel["india_civic_news"][:2]:
                b24_tickers.insert(0, f"NATIONAL WIRE: {item.get('title')} ({item.get('source', 'Desk')})")
        b24["breaking_ticker"] = b24_tickers[:5]

        # Dynamic Anchor Dialogue based on Circadian Phase
        if "Midnight" in circadian_phase:
            b24["studio_dialogue"] = f"It is {world_time} past midnight. The metropolis rests under starlit skies at {temp_str}. Night maintenance crews on Outer Ring Road and server operators at Manyata Tech Park remain active."
        elif "Dawn" in circadian_phase or "Early Morning" in circadian_phase:
            b24["studio_dialogue"] = f"Good early morning Bengaluru, time is {world_time}. Dawn mist envelops Cubbon Park at {temp_str}. Vidyarthi Bhavan and Brahmin's Coffee Bar begin chicory roasts as morning commuters assemble."
        elif "Afternoon" in circadian_phase:
            b24["studio_dialogue"] = f"Midday in the Silicon Plateau, time is {world_time} at {temp_str}. Cafeterias across Manyata and Ecospace are bustling. Silk Board traffic currently measured at {silk_congestion}% gridlock."
        else:
            b24["studio_dialogue"] = f"Live from MG Road, time is {world_time} ({circadian_phase}). Weather is holding at {temp_str} ({cond_str}). Commercial corridors across Church Street and Koramangala report high footfall."

        # 2. Update CNBC_BLR_TECH
        cnbc = self.channels["CNBC_BLR_TECH"]
        cnbc_tickers = []
        if stocks:
            stock_str = " | ".join([f"{s.get('symbol')}: ₹{s.get('price')} ({s.get('change')})" for s in stocks[:4]])
            cnbc_tickers.append(f"BLR-TECH-30 STOCKS: {stock_str}")
        
        if real_intel and "finance" in real_intel:
            fx = real_intel["finance"].get("usd_inr", 86.85)
            cnbc_tickers.append(f"REAL FOREX: USD/INR at ₹{fx} | Indian IT & SaaS margins benefit from resilient dollar conversion")

        if recent_fg_audit and recent_fg_audit.get("summary"):
            s = recent_fg_audit["summary"]
            p_name = s.get("target_product", "Innovation")
            verdict = s.get("consensus_verdict", "")
            cnbc_tickers.insert(0, f"AUDIT FLASH: '{p_name}' tested by 100-citizen focus group -> {verdict}")
            if s.get("is_commercial_failure"):
                cnbc["studio_dialogue"] = f"Special market alert: Synthetic focus group telemetry exposes critical commercial hurdles for '{p_name}'. 100 autonomous citizen personas rejected the pitch with unvarnished feedback cited on price resistance and hype skepticism."
        cnbc["breaking_ticker"] = cnbc_tickers[:5]

        # 3. Update METRO_AI_PULSE
        ai_pulse = self.channels["METRO_AI_PULSE"]
        ai_tickers = [
            "SYSTEMS ARCHITECTURE: Engram Alpha V4 POSIX shared memory ring buffers eliminate thread locks completely",
            "ENVIRONMENT TELEMETRY: Open-Meteo live atmospheric vectors streaming directly into Metropolis 3D Voxel Engine",
            "AUTONOMOUS COGNITION: Dual-speed PIANO architecture orchestrates 100 concurrent citizens with zero latency drift"
        ]
        if real_intel and "global_tech_news" in real_intel:
            for item in real_intel["global_tech_news"][:2]:
                ai_tickers.insert(0, f"GLOBAL TECH WIRE: {item.get('title')}")
        ai_pulse["breaking_ticker"] = ai_tickers[:5]

    def get_all_channels(self) -> Dict[str, Any]:
        return {
            "active_channel": self.active_channel,
            "channels": list(self.channels.values())
        }

TV_NETWORK = BengaluruTVBroadcastNetwork()
