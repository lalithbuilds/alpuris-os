"""
Bengaluru Living Agent Metropolis Engine (Namma Bengaluru)
- 100 Autonomous Citizens executing concurrently across 16 Iconic Bengaluru Sectors
- Real GPS Coordinates, Namma Metro Transit Lines, Silk Board Traffic Bottlenecks
- Living INR (₹) Economy + BLR-TECH-30 Stock Market & Startup Valuation Index
- Dynamic Real-Time Weather (Breeze, Monsoons, Lake Alerts) & Traffic Congestion Engine
- Namma Radio 91.1 FM Autonomous Broadcasts (RJ Disha & RJ Raaj)
- Municipal City Council Voting & The Bengaluru Chronicle Automated Tabloid
- PIANO Dual-Speed Concurrency (System-1 Reflex + System-2 Deliberate LLM)
- Governor "God Mode" Executive Console (City Broadcast + 1-on-1 Direct Citizen Calling)
"""

import os
import sys
import time
import json
import sqlite3
import random
import threading
import statistics
import concurrent.futures
from typing import List, Dict, Any, Optional, Tuple, Set

try:
    from ray_agent_world.cognitive_core import Persona, WorldClock
    from ray_agent_world.computer_skills import ComputerInterface
    from ray_agent_world.smallville_memory import AssociativeMemoryStream
    from ray_agent_world.voxel_world import VoxelWorldGrid, BLUEPRINTS, BLOCK_TYPES
    from ray_agent_world.social_and_market import SocialGraph, P2PContractMarket
    from ray_agent_world.life_and_economy_engine import LifeAndEconomyEngine
    from ray_agent_world.consumer_marketing_engine import ConsumerMarketingEngine
    from ray_agent_world.realtime_data_feed import HARVESTER
    from ray_agent_world.live_tv_network import TV_NETWORK
    from ray_agent_world.metropolis_social_and_community import SOCIAL_OS, COMMUNITY_GROUPS
    from ray_agent_world.mortality_and_lifecycle_engine import LifecycleAndMortalityEngine
    from ray_agent_world.sandboxed_execution_engine import SandboxedExecutionEngine
    from ray_agent_world.ad_creative_and_visual_engine import AdCreativeAndVisualEngine
    from ray_agent_world.spatial_diffusion_engine import SpatialDiffusionEngine
    from ray_agent_world.citizen_vector_brain import CitizenVectorBrain
    from ray_agent_world.webhook_bridge import WebhookBridge
    from ray_agent_world.citizen_homes_and_housing_engine import CitizenHousingEngine
    from ray_agent_world.citizen_smartphone_engine import CitizenSmartphoneEngine
    from ray_agent_world.urban_fauna_and_parks_engine import UrbanFaunaAndParksEngine
except ModuleNotFoundError:
    from cognitive_core import Persona, WorldClock
    from computer_skills import ComputerInterface
    from smallville_memory import AssociativeMemoryStream
    from voxel_world import VoxelWorldGrid, BLUEPRINTS, BLOCK_TYPES
    from social_and_market import SocialGraph, P2PContractMarket
    from life_and_economy_engine import LifeAndEconomyEngine
    from consumer_marketing_engine import ConsumerMarketingEngine
    from realtime_data_feed import HARVESTER
    from live_tv_network import TV_NETWORK
    from metropolis_social_and_community import SOCIAL_OS, COMMUNITY_GROUPS
    from mortality_and_lifecycle_engine import LifecycleAndMortalityEngine
    from sandboxed_execution_engine import SandboxedExecutionEngine
    from ad_creative_and_visual_engine import AdCreativeAndVisualEngine
    from spatial_diffusion_engine import SpatialDiffusionEngine
    from citizen_vector_brain import CitizenVectorBrain
    from webhook_bridge import WebhookBridge
    from citizen_homes_and_housing_engine import CitizenHousingEngine
    from citizen_smartphone_engine import CitizenSmartphoneEngine
    from urban_fauna_and_parks_engine import UrbanFaunaAndParksEngine

DB_PATH = "/Users/lalith/ray_agent_world/world_memory.sqlite"
WORKSPACE_DIR = "/Users/lalith/ray_agent_world/workspace"

# Detailed Bengaluru Spatial Sectors with Real GPS Coordinates
ZONE_METADATA = {
    "Kempegowda_Airport_BLR": {"name": "✈️ BLR Airport (KIA)", "category": "Aviation", "lat": 13.1986, "lon": 77.7066, "color": "#e3b341", "metro": "Airport Blue Line", "desc": "International Terminal 1 & 2 Global Business Gateway"},
    "Manyata_Tech_Park": {"name": "🏢 Manyata Tech Park", "category": "Tech Park", "lat": 13.0498, "lon": 77.6200, "color": "#58a6ff", "metro": "Airport Blue Line", "desc": "Outer Ring Road IT & Cloud Infrastructure Hub"},
    "IISc_Research_Campus": {"name": "🔬 IISc Deep Tech Labs", "category": "Research", "lat": 13.0219, "lon": 77.5671, "color": "#79c0ff", "metro": "Green Line", "desc": "Indian Institute of Science Quantum & Neuromorphic Labs"},
    "Whitefield_ITPB": {"name": "🌐 Whitefield ITPB", "category": "Tech Park", "lat": 12.9863, "lon": 77.7340, "color": "#388bfd", "metro": "Purple Line", "desc": "International Tech Park Bangalore Enterprise AI Hub"},
    "Bagmane_Tech_Park": {"name": "💻 Bagmane Tech Park", "category": "Tech Park", "lat": 12.9793, "lon": 77.6576, "color": "#58a6ff", "metro": "Purple Line", "desc": "CV Raman Nagar Software & Biotech Campus"},
    "Indiranagar_100ft_Startups": {"name": "🚀 Indiranagar Startups", "category": "Startups", "lat": 12.9719, "lon": 77.6412, "color": "#bc8cff", "metro": "Purple Line", "desc": "100ft Road AI Studios, Modern Web & Micro-Breweries"},
    "Vidhana_Soudha_Capitol": {"name": "🏛️ Vidhana Soudha", "category": "Governance", "lat": 12.9797, "lon": 77.5909, "color": "#7ee787", "metro": "Purple Line", "desc": "State Secretariat, High Court & City Mayor Council"},
    "Cubbon_Park_Canopy": {"name": "🌳 Cubbon Park Canopy", "category": "Green Space", "lat": 12.9763, "lon": 77.5929, "color": "#2ea043", "metro": "Purple Line", "desc": "300-Acre Historic Botanical Sanctuary & Reflection Groves"},
    "Church_Street_Cafes": {"name": "☕ Church Street Cafes", "category": "Culture", "lat": 12.9748, "lon": 77.6074, "color": "#f0883e", "metro": "Purple Line", "desc": "Bookstores, Artisan Cafes & Press Room Walkway"},
    "UB_City_Luxury_Towers": {"name": "💎 UB City Towers", "category": "Fintech & VC", "lat": 12.9716, "lon": 77.5957, "color": "#d29922", "metro": "Purple Line", "desc": "Vittal Mallya Road Commercial High-Rises & VC Boardrooms"},
    "Majestic_Metro_Interchange": {"name": "🚇 Majestic Metro Hub", "category": "Transit", "lat": 12.9756, "lon": 77.5728, "color": "#3fb950", "metro": "Purple & Green Hub", "desc": "Central Namma Metro Interchange & Inter-City Terminals"},
    "Gandhi_Bazaar_Heritage": {"name": "☕ Gandhi Bazaar Heritage", "category": "Heritage", "lat": 12.9438, "lon": 77.5693, "color": "#db6d28", "metro": "Green Line", "desc": "Historic Basavanagudi Vidyarthi Bhavan & Culinary Culture"},
    "Nexus_Koramangala_Mall": {"name": "🛍️ Koramangala Mall", "category": "Commercial", "lat": 12.9352, "lon": 77.6245, "color": "#e3b341", "metro": "Feeder Bus", "desc": "Koramangala 7th Block Retail & Fintech Meeting Grounds"},
    "Silk_Board_Junction": {"name": "🚦 Silk Board Flyover", "category": "Transit", "lat": 12.9174, "lon": 77.6229, "color": "#f85149", "metro": "ORR Bus Rapid", "desc": "Silk Board Transit Choke Point & High-Density Intersection"},
    "HSR_Layout_Residences": {"name": "🏡 HSR Layout Homes", "category": "Residential", "lat": 12.9121, "lon": 77.6446, "color": "#a371f7", "metro": "Feeder Metro", "desc": "Sectors 1-7 Co-Living Homes & Apartments"},
    "Electronic_City_Phase_1": {"name": "🖥️ Electronic City Hub", "category": "Tech Campus", "lat": 12.8399, "lon": 77.6770, "color": "#388bfd", "metro": "Yellow Line", "desc": "Phase 1 Microelectronics, Hardware & Cyber Security Campus"},
    "Koramangala_Microbrewery_Pub": {"name": "🍺 Koramangala Brewery & Pub", "category": "Nightlife & Pubs", "lat": 12.9344, "lon": 77.6190, "color": "#f59e0b", "metro": "Feeder Bus", "desc": "Artisan Craft Beer Brewery, Rooftop Taprooms & Hops Tanks"},
    "HSR_Cult_Fit_Gym": {"name": "🏋️ HSR Cult.fit Elite Gym", "category": "Wellness & Gyms", "lat": 12.9100, "lon": 77.6400, "color": "#ef4444", "metro": "Feeder Metro", "desc": "Olympic Lifting Platforms, High-Tech Treadmills & Strength Racks"},
    "MG_Road_Boulevard": {"name": "🚌 MG Road BMTC & Metro Hub", "category": "Transit Boulevard", "lat": 12.9750, "lon": 77.6090, "color": "#06b6d4", "metro": "Purple Line", "desc": "Central Promenade, BMTC Electric Bus Fleet Terminal & Pedestrian Plaza"},
    "Bull_Temple_Basavanagudi": {"name": "🛕 Bull Temple (Dodda Basavana Gudi)", "category": "Heritage & Temple", "lat": 12.9423, "lon": 77.5681, "color": "#f59e0b", "metro": "Green Line", "desc": "Sacred 16th-Century Dravidian Temple, Monolithic Nandi Shrine & Kadalekai Parishe Grounds"},
    "St_Marks_Cathedral_Churches": {"name": "⛪ St. Mark's Cathedral & Community", "category": "Faith & Fellowship", "lat": 12.9734, "lon": 77.6030, "color": "#60a5fa", "metro": "Purple Line", "desc": "Historic 1808 English Baroque Cathedral, Sunday Choir, Fellowship Hall & Community Garden"},
    "Dev_Coliving_Citizen_Residences": {"name": "🏘️ Dev Co-Living PG & Citizen Homes", "category": "Residential Communities", "lat": 12.9730, "lon": 77.6350, "color": "#ec4899", "metro": "Purple Line", "desc": "Modern 4-Story Co-Living Apartments, Rooftop Garden Lounge & Community Kitchen"},
    "Bengaluru_Care_Hospital_Clinic": {"name": "🏥 Narayana Health Care Clinic", "category": "Healthcare & Wellness", "lat": 12.9250, "lon": 77.6300, "color": "#10b981", "metro": "Feeder Bus", "desc": "24/7 Community Clinic, Emergency Ambulance Bay, Child Care & Wellness Consultations"}
}

BENGALURU_ZONES = list(ZONE_METADATA.keys())

# Scaled canvas coordinate layout (1000 x 750)
ZONE_COORDINATES = {
    "Kempegowda_Airport_BLR": {"x": 480, "y": 45, "w": 180, "h": 65, "color": "#e3b341", "name": "✈️ BLR Airport (KIA)"},
    "Manyata_Tech_Park": {"x": 750, "y": 140, "w": 180, "h": 75, "color": "#58a6ff", "name": "🏢 Manyata Tech Park"},
    "IISc_Research_Campus": {"x": 180, "y": 150, "w": 180, "h": 75, "color": "#79c0ff", "name": "🔬 IISc Deep Tech Labs"},
    "Majestic_Metro_Interchange": {"x": 160, "y": 270, "w": 180, "h": 75, "color": "#3fb950", "name": "🚇 Majestic Metro Hub"},
    "Vidhana_Soudha_Capitol": {"x": 420, "y": 260, "w": 170, "h": 75, "color": "#7ee787", "name": "🏛️ Vidhana Soudha"},
    "Cubbon_Park_Canopy": {"x": 650, "y": 260, "w": 160, "h": 75, "color": "#2ea043", "name": "🌳 Cubbon Park Canopy"},
    "Whitefield_ITPB": {"x": 800, "y": 320, "w": 170, "h": 75, "color": "#388bfd", "name": "🌐 Whitefield ITPB"},
    "Church_Street_Cafes": {"x": 440, "y": 370, "w": 170, "h": 75, "color": "#f0883e", "name": "☕ Church Street Cafes"},
    "UB_City_Luxury_Towers": {"x": 220, "y": 390, "w": 170, "h": 75, "color": "#d29922", "name": "💎 UB City Towers"},
    "Bagmane_Tech_Park": {"x": 720, "y": 410, "w": 170, "h": 70, "color": "#58a6ff", "name": "💻 Bagmane Tech Park"},
    "Indiranagar_100ft_Startups": {"x": 780, "y": 500, "w": 170, "h": 75, "color": "#bc8cff", "name": "🚀 Indiranagar Startups"},
    "Gandhi_Bazaar_Heritage": {"x": 120, "y": 510, "w": 180, "h": 75, "color": "#db6d28", "name": "☕ Gandhi Bazaar Heritage"},
    "Nexus_Koramangala_Mall": {"x": 660, "y": 580, "w": 170, "h": 75, "color": "#e3b341", "name": "🛍️ Koramangala Mall"},
    "Silk_Board_Junction": {"x": 380, "y": 560, "w": 180, "h": 75, "color": "#f85149", "name": "🚦 Silk Board Flyover"},
    "HSR_Layout_Residences": {"x": 760, "y": 665, "w": 170, "h": 70, "color": "#a371f7", "name": "🏡 HSR Layout Homes"},
    "Electronic_City_Phase_1": {"x": 280, "y": 665, "w": 180, "h": 70, "color": "#388bfd", "name": "🖥️ Electronic City Hub"},
    "Koramangala_Microbrewery_Pub": {"x": 560, "y": 490, "w": 180, "h": 70, "color": "#f59e0b", "name": "🍺 Koramangala Brewery & Pub"},
    "HSR_Cult_Fit_Gym": {"x": 800, "y": 600, "w": 170, "h": 70, "color": "#ef4444", "name": "🏋️ HSR Cult.fit Elite Gym"},
    "MG_Road_Boulevard": {"x": 320, "y": 320, "w": 170, "h": 65, "color": "#06b6d4", "name": "🚌 MG Road BMTC & Metro Hub"},
    "Bull_Temple_Basavanagudi": {"x": 120, "y": 600, "w": 180, "h": 70, "color": "#f59e0b", "name": "🛕 Bull Temple (Dodda Basavana Gudi)"},
    "St_Marks_Cathedral_Churches": {"x": 520, "y": 300, "w": 180, "h": 65, "color": "#60a5fa", "name": "⛪ St. Mark's Cathedral & Community"},
    "Dev_Coliving_Citizen_Residences": {"x": 620, "y": 480, "w": 170, "h": 70, "color": "#ec4899", "name": "🏘️ Dev Co-Living PG & Citizen Homes"},
    "Bengaluru_Care_Hospital_Clinic": {"x": 480, "y": 640, "w": 180, "h": 70, "color": "#10b981", "name": "🏥 Narayana Health Care Clinic"}
}

METRO_LINES = [
    # Purple Line: Majestic -> Vidhana Soudha -> Church Street -> Indiranagar -> Whitefield
    [{"x": 250, "y": 307}, {"x": 505, "y": 297}, {"x": 525, "y": 407}, {"x": 865, "y": 537}, {"x": 885, "y": 357}],
    # Green/Yellow Line: IISc -> Majestic -> Silk Board -> Electronic City
    [{"x": 270, "y": 187}, {"x": 250, "y": 307}, {"x": 470, "y": 597}, {"x": 370, "y": 700}],
    # Airport Blue Line: Majestic -> Manyata -> BLR Airport
    [{"x": 250, "y": 307}, {"x": 840, "y": 177}, {"x": 570, "y": 77}]
]

# Municipal City Bills Engine
CITY_BILLS = [
    {"id": "BILL_101", "title": "Namma Metro 24/7 Operations Ordinance", "status": "VOTING", "yes_votes": 48, "no_votes": 12, "desc": "Expand Purple and Green lines to run 24 hours to alleviate road congestion."},
    {"id": "BILL_102", "title": "Silk Board Elevated Toll Subsidy (₹40)", "status": "PASSED", "yes_votes": 74, "no_votes": 26, "desc": "Subsidize electric public transit to bypass Silk Board bottleneck."},
    {"id": "BILL_103", "title": "Commercial AI Server Energy Subsidy", "status": "VOTING", "yes_votes": 62, "no_votes": 28, "desc": "15% tariff reduction for green energy datacenters in Manyata and Electronic City."},
    {"id": "BILL_104", "title": "Cubbon Park Weekend Motor Ban", "status": "PASSED", "yes_votes": 88, "no_votes": 12, "desc": "Total vehicle prohibition in Cubbon Park on Saturdays and Sundays."}
]

# BLR-TECH-30 Stock Market & Startup Index
INITIAL_STOCKS = [
    {"symbol": "INFX", "name": "Infosys Tech Ltd", "price": 1585.0, "change": "+1.4%", "sector": "IT & Cloud", "volume": "1.2M"},
    {"symbol": "ZROD", "name": "Zerodha Broking", "price": 4250.0, "change": "+2.1%", "sector": "Fintech", "volume": "840K"},
    {"symbol": "SWGY", "name": "Swiggy Hyperlocal", "price": 492.0, "change": "-0.8%", "sector": "Consumer Tech", "volume": "3.1M"},
    {"symbol": "AURA", "name": "Aura Autonomous AI", "price": 845.0, "change": "+6.4%", "sector": "Agentic AI", "volume": "980K"},
    {"symbol": "PEAK", "name": "PeakXV Ventures Fund", "price": 12400.0, "change": "+0.5%", "sector": "Venture Capital", "volume": "120K"},
    {"symbol": "YATR", "name": "Namma Yatri Mobility", "price": 315.0, "change": "+4.2%", "sector": "Open Transit", "volume": "1.5M"},
    {"symbol": "QNTM", "name": "IISc Quantum Foundry", "price": 1120.0, "change": "+3.8%", "sector": "Deep Tech", "volume": "410K"},
    {"symbol": "AERO", "name": "Kempegowda Aerospace", "price": 2480.0, "change": "+1.1%", "sector": "Aviation", "volume": "620K"}
]
BASE_STOCK_PRICES = {s["symbol"]: float(s["price"]) for s in INITIAL_STOCKS}

# Dynamic Bengaluru Weather Simulation
WEATHER_STATES = [
    {"temp": "23°C", "condition": "Gentle Breeze & Mild Sunshine", "humidity": "58%", "aqi": 48, "desc": "Iconic pleasant Bengaluru weather across Cubbon Park"},
    {"temp": "27°C", "condition": "Warm Afternoon Sun", "humidity": "62%", "aqi": 62, "desc": "Active business rush across Manyata and Electronic City"},
    {"temp": "19°C", "condition": "Pre-Monsoon Cloudburst", "humidity": "88%", "aqi": 32, "desc": "Rainwater runoff along Indiranagar 100ft Road and Silk Board"},
    {"temp": "18°C", "condition": "Cool Evening Breeze", "humidity": "70%", "aqi": 41, "desc": "Outdoor cafes on Church Street bustling with lively conversations"},
    {"temp": "16°C", "condition": "Morning Radiation Mist", "humidity": "82%", "aqi": 55, "desc": "Early flights touching down at Kempegowda International Airport"}
]

class MetropolisEventBus:
    """
    Unified Publish/Subscribe Event Bus for emergent city events across all 16 sectors.
    Decouples real-time civic events, macro triggers, economic shocks, and citizen reactions.
    """
    def __init__(self, max_history: int = 250):
        self.subscribers: Dict[str, List[Any]] = {}
        self.history: List[Dict[str, Any]] = []
        self.max_history = max_history
        self._lock = threading.Lock()

    def subscribe(self, topic: str, handler: Any):
        with self._lock:
            self.subscribers.setdefault(topic, []).append(handler)

    def publish(self, topic: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        with self._lock:
            import uuid
            event = {
                "id": str(uuid.uuid4())[:8],
                "topic": topic,
                "payload": payload,
                "timestamp": time.time(),
                "time_str": time.strftime("%H:%M:%S")
            }
            self.history.append(event)
            if len(self.history) > self.max_history:
                self.history.pop(0)
            handlers = list(self.subscribers.get(topic, [])) + list(self.subscribers.get("*", []))

        for h in handlers:
            try:
                h(event)
            except Exception:
                pass
        return event

    def get_recent(self, limit: int = 50, topic: Optional[str] = None) -> List[Dict[str, Any]]:
        with self._lock:
            if topic:
                filtered = [e for e in self.history if e["topic"] == topic]
            else:
                filtered = list(self.history)
            return filtered[-limit:]

class LivingWorld:
    def __init__(self):
        self.computer = ComputerInterface()
        self.clock = WorldClock(start_hour=9, start_minute=0)
        self.x11_lock = threading.Lock()
        self.db_lock = threading.Lock()
        self.event_bus = MetropolisEventBus()
        self.personas: Dict[str, Persona] = {}
        self.tick_count = 0
        self.world_time = time.time()
        self.last_conversations: List[Dict[str, Any]] = []
        self.chronicle_headlines: List[Dict[str, Any]] = []
        self.city_bills = list(CITY_BILLS)
        self.bill_voter_ids: Dict[str, Set[str]] = {}
        self.stocks = [dict(s) for s in INITIAL_STOCKS]
        self.weather = dict(WEATHER_STATES[0])
        self.silk_board_congestion = 78
        self.radio_broadcasts: List[Dict[str, Any]] = []
        self.voxel_world = VoxelWorldGrid()
        self.social_graph = SocialGraph()
        self.p2p_market = P2PContractMarket()
        self.life_economy = LifeAndEconomyEngine()
        self.consumer_marketing = ConsumerMarketingEngine()
        self.realtime_harvester = HARVESTER
        self.tv_network = TV_NETWORK
        self.social_os = SOCIAL_OS
        self.lifecycle_engine = LifecycleAndMortalityEngine()
        self.sandbox_engine = SandboxedExecutionEngine()
        self.creative_engine = AdCreativeAndVisualEngine()
        self.spatial_diffusion = SpatialDiffusionEngine()
        self.vector_brain = CitizenVectorBrain()
        self.webhook_bridge = WebhookBridge()
        self.housing_engine = CitizenHousingEngine()
        self.smartphone_engine = CitizenSmartphoneEngine()
        self.fauna_engine = UrbanFaunaAndParksEngine()
        os.makedirs(WORKSPACE_DIR, exist_ok=True)
        self.init_db()
        self._spawn_all_100_citizens()
        self.housing_engine.assign_homes_to_citizens(self.personas)
        self.smartphone_engine.initialize_citizen_phones(self.personas)

    def init_db(self):
        with self.db_lock:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("PRAGMA journal_mode=WAL;")
            cur.execute("""
                CREATE TABLE IF NOT EXISTS world_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tick INTEGER,
                    persona_id TEXT,
                    persona_name TEXT,
                    department TEXT,
                    zone TEXT,
                    action TEXT,
                    arousal REAL,
                    timestamp REAL
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS world_conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tick INTEGER,
                    world_time TEXT,
                    zone TEXT,
                    speaker_1 TEXT,
                    speaker_2 TEXT,
                    turn_1 TEXT,
                    turn_2 TEXT,
                    affinity REAL,
                    timestamp REAL
                )
            """)
            conn.commit()
            conn.close()

    def _spawn_all_100_citizens(self):
        citizens = [
            # Guild 1: Cloud & Distributed Systems (Manyata Tech Park)
            ("AARAV", "Aarav Sharma", "Chief Systems Architect", "Manyata_Tech_Park", "Core Architecture", "Architect of ZeroMQ message rings & memory arenas"),
            ("ROHAN", "Rohan Gupta", "Distributed Storage Lead", "Manyata_Tech_Park", "Core Architecture", "Expert in POSIX shared memory and SQLite WAL performance"),
            ("KABIR", "Kabir Menon", "Principal Cloud SRE", "Manyata_Tech_Park", "DevOps & Infrastructure", "Kubernetes cluster manager across Manyata data centers"),
            ("POOJA", "Pooja Hegde", "Postgres & WAL Performance DBA", "Manyata_Tech_Park", "DevOps & Infrastructure", "Optimizes zero-latency database transactions"),
            ("NEHA", "Neha Reddy", "Build Automation Lead", "Manyata_Tech_Park", "DevOps & Infrastructure", "Maintains CI/CD release hygiene across Bengaluru repos"),

            # Guild 2: AI Startups & Autonomous Compilers (Indiranagar Startups)
            ("PRIYA", "Priya Patel", "Lead UI/UX Systems Engineer", "Indiranagar_100ft_Startups", "UI & Frontend Systems", "Creator of real-time Glassmorphism Canvas telemetry"),
            ("ANANYA", "Ananya Roy", "Compilers & AST Specialist", "Indiranagar_100ft_Startups", "Code Synthesis", "Transforms abstract syntax trees for autonomous agents"),
            ("ISHA", "Isha Sengupta", "Autonomous Web Scraper Lead", "Indiranagar_100ft_Startups", "Market Intelligence", "Scrapes tech trends, GitHub, and HackerNews in real-time"),
            ("VARUN", "Varun Saxena", "Developer Experience Lead", "Indiranagar_100ft_Startups", "Developer Tools", "Optimizes terminal interfaces and human-agent ergonomics"),
            ("SIDDHARTH", "Siddharth Nair", "Model Benchmark Lead", "Indiranagar_100ft_Startups", "Market Intelligence", "Evaluates frontier LLM latency, reasoning, and token pricing"),

            # Guild 3: Deep Tech, Quantum & Academic Research (IISc Campus)
            ("PROF_RAMAN", "Dr. K. Ramanathan", "Chair of Quantum Computing", "IISc_Research_Campus", "Academic Research", "Researches topological quantum computing algorithms"),
            ("TANYA", "Tanya Joshi", "ArXiv Multi-Agent Scout", "IISc_Research_Campus", "Academic Research", "Indexes frontier multi-agent consensus literature"),
            ("ANIRUDH", "Anirudh Deshpande", "Neuromorphic Silicon Fellow", "IISc_Research_Campus", "Hardware R&D", "Develops spiking neural network processors"),
            ("SHRUTI", "Shruti Vaidya", "Bioinformatics Fellow", "IISc_Research_Campus", "Academic Research", "Applies protein folding embeddings to drug discovery"),
            ("ADITYA", "Aditya Rao", "Token Economics & FinOps Lead", "IISc_Research_Campus", "Economic Research", "Simulates agent token budgets and inference cost arbitrage"),

            # Guild 4: Enterprise IT, Hardware & Embedded Systems (Electronic City)
            ("KARTHIK", "Karthik Iyer", "Low-Latency Protocols Lead", "Electronic_City_Phase_1", "Core Architecture", "Engineers sub-millisecond edge network sockets"),
            ("CHETAN", "Chetan Gowda", "FPGA & ASIC Hardware Engineer", "Electronic_City_Phase_1", "Hardware R&D", "Designs hardware accelerators for local LLM inference"),
            ("MANOJ", "Manoj Kulkarni", "Embedded RTOS Firmware Lead", "Electronic_City_Phase_1", "Hardware R&D", "Develops safety-critical real-time OS kernels"),
            ("HARINI", "Harini Murthy", "Edge Sensor Mesh Coordinator", "Electronic_City_Phase_1", "Hardware R&D", "Monitors thousands of smart city telemetry sensors"),
            ("FARHAN", "Farhan Ali", "Chaos & Fault Injection Engineer", "Electronic_City_Phase_1", "DevOps & Infrastructure", "Simulates container drops and power blackout drills"),

            # Guild 5: Cyber Defense, Red Teaming & Forensics (Electronic City & Whitefield)
            ("VIKRAM", "Vikram Verma", "Chief Information Security Officer", "Electronic_City_Phase_1", "Cyber Defense", "Audits campus firewalls, port boundaries, and threat vectors"),
            ("MEERA", "Meera Nambiar", "Red Team Lead & Threat Modeler", "Whitefield_ITPB", "Cyber Defense", "Simulates sandbox escapes and prompt injection guards"),
            ("ARJUN", "Arjun Kapoor", "Cryptographic Integrity Auditor", "Whitefield_ITPB", "Cyber Defense", "Validates mTLS keys, HMAC signatures, and hardware security modules"),
            ("SNEHA", "Sneha Kulkarni", "Data Privacy & Compliance Officer", "Electronic_City_Phase_1", "Cyber Defense", "Enforces PII redaction and telemetry scrubbing"),
            ("DEV", "Dev Mathur", "Forensic Reverse Engineer", "Whitefield_ITPB", "Cyber Defense", "Analyzes binary dumps, syscall traces, and zero-day vulnerabilities"),

            # Guild 6: Venture Capital, Fintech & Markets (UB City & Koramangala)
            ("RAJESH", "Rajesh Goel", "Managing Partner at PeakXV", "UB_City_Luxury_Towers", "Venture Capital", "Invests in enterprise AI, infrastructure, and developer tools"),
            ("MEGHA", "Megha Singhania", "Fintech Risk & Liquidity Director", "UB_City_Luxury_Towers", "Fintech", "Manages high-frequency algorithmic liquidity in ₹ INR"),
            ("ZOYA", "Zoya Deshmukh", "Lead Market Intel Analyst", "UB_City_Luxury_Towers", "Market Intelligence", "Monitors global tech capital flows and M&A trends"),
            ("PRANAV", "Pranav Bajaj", "Angel Investor & Syndicate Lead", "Nexus_Koramangala_Mall", "Venture Capital", "Backs pre-seed deeptech and AI agent startups"),
            ("DIVYA", "Divya Narang", "Quantitative DeFi Strategist", "Nexus_Koramangala_Mall", "Fintech", "Designs automated market-making and liquidity pools"),

            # Guild 7: City Governance, Law & Ethics (Vidhana Soudha)
            ("TARA", "Tara Sen", "City Mayor & Governance Director", "Vidhana_Soudha_Capitol", "City Administration", "Coordinates municipal technology roadmaps and ordinances"),
            ("NIKHIL", "Nikhil Varma", "City Ethics & Alignment Governor", "Vidhana_Soudha_Capitol", "City Administration", "Enforces AI ethical alignment and transparency guidelines"),
            ("JUSTICE_RAO", "Justice M. Rao", "High Court Senior Jurist", "Vidhana_Soudha_Capitol", "Judiciary", "Presides over algorithmic accountability and digital rights"),
            ("ANAND", "Anand Patil", "BBMP Municipal Commissioner", "Vidhana_Soudha_Capitol", "City Administration", "Oversees urban infrastructure, roads, and civic sanitation"),
            ("MAYA", "Maya Sundaram", "City Resource Allocation Chief", "Vidhana_Soudha_Capitol", "City Administration", "Allocates power grid quotas, fiber routes, and municipal funds"),

            # Guild 8: Transit, Namma Metro & Urban Logistics (Majestic & Silk Board)
            ("SAMIR", "Samir Bhat", "Namma Metro Operations Director", "Majestic_Metro_Interchange", "Transit Logistics", "Oversees train frequencies, signaling, and passenger safety"),
            ("RITU", "Ritu Chopra", "Urban Traffic & Safety Inspector", "Silk_Board_Junction", "Transit Logistics", "Monitors Silk Board congestion and automated traffic lights"),
            ("SURESH", "Suresh Gowda", "BMTC Electric Bus Dispatcher", "Majestic_Metro_Interchange", "Transit Logistics", "Dispatches electric feeder buses across metro corridors"),
            ("GANESH", "Ganesh Kumar", "Senior Metro Loco Pilot", "Majestic_Metro_Interchange", "Transit Logistics", "Pilots Purple Line trains between Whitefield and Kengeri"),
            ("KRISHNA", "Krishna Murthy", "Auto-Rickshaw Union President", "Silk_Board_Junction", "Transit Logistics", "Coordinates last-mile meter fares and driver welfare"),

            # Guild 9: Journalism, Media & Investigative Press (Church Street Press Room)
            ("RHEA", "Rhea Kapoor", "Senior Editor @ The Bengaluru Chronicle", "Church_Street_Cafes", "Media & Press", "Breaks frontline tech stories, municipal audits, and news"),
            ("VIVEK", "Vivek Menon", "Cybercrime Investigative Reporter", "Church_Street_Cafes", "Media & Press", "Investigates zero-day leaks, corporate breaches, and scams"),
            ("SUNITA", "Sunita Sen", "City Photojournalist & Documentarian", "Church_Street_Cafes", "Media & Press", "Captures the human stories of Bengaluru's digital transformation"),
            ("AMIT", "Amitabh Roy", "Technology & Economics Columnist", "Church_Street_Cafes", "Media & Press", "Writes weekly op-eds on AI capital and urban planning"),
            ("DEEPA", "Deepa Shankar", "Weather & Traffic Live Reporter", "Church_Street_Cafes", "Media & Press", "Provides live broadcast reports on Silk Board delays and monsoons"),

            # Guild 10: Culture, Hospitality & Culinary Heritage (Gandhi Bazaar & Church Street)
            ("RAMESH", "Ramesh Bhat", "Head Chef @ Vidyarthi Bhavan", "Gandhi_Bazaar_Heritage", "Culinary Heritage", "Master of iconic crispy benne dosas and South Indian filter coffee"),
            ("KAVITA", "Kavita Rao", "Independent Bookstore Curator", "Church_Street_Cafes", "Culture & Literature", "Hosts literary salons and underground tech philosophy circles"),
            ("SACHIN", "Sachin Hegde", "Specialty Coffee Roaster", "Church_Street_Cafes", "Culinary Arts", "Roasts single-estate Chikmagalur beans for tech founders"),
            ("LAKSHMI", "Lakshmi Amma", "HSR Resident Welfare President", "HSR_Layout_Residences", "Civic Community", "Champions neighborhood tree planting, composting, and solar panels"),
            ("TEJAS", "Tejas Srinivas", "Boutique Sound & Acoustics Designer", "Bagmane_Tech_Park", "Creative Arts", "Composes ambient soundscapes and acoustic audio environments"),

            # Guild 11: Space Tech & Satellite Guidance (ISRO / URSC / Bagmane)
            ("SIVAN", "Dr. K. Sivanathan", "Senior Director @ ISRO Satellite Systems", "Bagmane_Tech_Park", "Space Technologies", "Oversees geostationary orbit guidance and propulsion controls"),
            ("PALLAVI", "Pallavi Rao", "Cryogenic Propulsion Specialist", "Bagmane_Tech_Park", "Space Technologies", "Engineers cryogenic upper stages for heavy-lift launch vehicles"),
            ("SIDDHARTH_ISRO", "Siddharth Varma", "Deep Space Telemetry Lead", "Manyata_Tech_Park", "Space Technologies", "Processes lunar and interplanetary radio telemetry"),
            ("ANITA", "Dr. Anita Nair", "Remote Sensing Scientist", "IISc_Research_Campus", "Space Technologies", "Analyzes multispectral satellite imagery for urban Bangalore ecology"),
            ("MOHIT", "Mohit Deshmukh", "Payload Integration Specialist", "Bagmane_Tech_Park", "Space Technologies", "Integrates optical synthetic aperture radar into orbital satellites"),

            # Guild 12: Biotech, Genomics & Healthcare (Biocon & Narayana Health)
            ("SUNITA_BIO", "Dr. Sunita Mazumdar", "Chief Genomics Scientist @ Biocon", "Electronic_City_Phase_1", "Biotechnology", "Leads automated high-throughput DNA sequencing pipelines"),
            ("DEVRAJ", "Dr. Devraj Hegde", "Cardiothoracic AI Diagnostics Lead", "Electronic_City_Phase_1", "Healthcare AI", "Validates computer vision models for heart pathology screenings"),
            ("SHREYA", "Shreya Bannerjee", "Bioinformatics Pipeline Architect", "IISc_Research_Campus", "Biotechnology", "Constructs distributed genomic variant analysis clusters"),
            ("NARESH", "Dr. Naresh Gowda", "Clinical Trials Data Controller", "Electronic_City_Phase_1", "Healthcare AI", "Audits double-blind clinical telemetry for oncology therapeutics"),
            ("KALPANA", "Kalpana Swaminathan", "Synthetic Biology Specialist", "IISc_Research_Campus", "Biotechnology", "Synthesizes bio-enzymes for green industrial manufacturing"),

            # Guild 13: Gig Economy, Mobility & Smart City Logistics (Namma Yatri & Swiggy)
            ("SHANKAR", "Shankar Gowda", "Namma Yatri Union Convener", "Silk_Board_Junction", "Urban Mobility", "Advocates for open mobility protocol and commission-free driver rides"),
            ("DINESH", "Dinesh Kumar", "Top-Rated Electric Auto Pilot", "Majestic_Metro_Interchange", "Urban Mobility", "Navigates 40+ daily commutes across central Bangalore corridors"),
            ("MANJU", "Manjunath Reddy", "Hyperlocal Delivery Fleet Lead", "Indiranagar_100ft_Startups", "Urban Logistics", "Optimizes rapid delivery routes across East Bengaluru"),
            ("VINAY", "Vinay Prasad", "BMRCL Station Controller", "Indiranagar_100ft_Startups", "Transit Logistics", "Maintains crowd flow and ticket turnstiles at Indiranagar Metro"),
            ("REVATHI", "Revathi S.", "EV Battery Swapping Manager", "Silk_Board_Junction", "Green Energy", "Oversees automated 2-minute battery swaps for commercial 3-wheelers"),

            # Guild 14: Legal, Regulatory & Civic Activism (Vidhana Soudha & Whitefield)
            ("HARISH", "Harish Salve-Bhatt", "Senior Technology Counsel", "Vidhana_Soudha_Capitol", "Legal & IP", "Advises Karnataka government on AI copyright and algorithmic liability"),
            ("GEETA", "Geeta Menon", "Co-Founder @ Whitefield Rising", "Whitefield_ITPB", "Civic Activism", "Leads grassroots suburban commuter advocacy and lake conservation"),
            ("PRADEEP", "Pradeep Alva", "K-RERA Compliance Regulator", "Vidhana_Soudha_Capitol", "Urban Governance", "Monitors commercial tech park building compliance and zoning"),
            ("ARCHANA", "Archana Iyer", "Open Data & Civic Budget Activist", "Cubbon_Park_Canopy", "Civic Activism", "Publishes open visual charts of BBMP municipal tax expenditures"),
            ("BALAJI", "Balaji Vishwanathan", "Bengaluru Lakes Restoration Trustee", "Cubbon_Park_Canopy", "Environmental Science", "Engineers aeration and wetland bioswales to revive Bellandur Lake"),

            # Guild 15: Developer Relations, Compilers & AI Benchmarks (Indiranagar & Whitefield)
            ("ABHISHEK", "Abhishek Poddar", "VP Developer Relations", "Indiranagar_100ft_Startups", "Developer Relations", "Organizes hackathons and developer meetups across Bengaluru"),
            ("SANYA", "Sanya Mirza", "Principal Interaction Designer", "Indiranagar_100ft_Startups", "UI & Frontend Systems", "Designs micro-interactions and high-density spatial layouts"),
            ("CHANDRU", "Chandrashekhar Rao", "LLVM & JIT Compiler Engineer", "Whitefield_ITPB", "Core Architecture", "Compiles domain-specific neural network kernels for edge NPUs"),
            ("RADHIKA", "Radhika Sen", "Agentic AI Benchmark Evaluator", "Indiranagar_100ft_Startups", "Market Intelligence", "Evaluates tool-use reliability and context drift in multi-agent models"),
            ("KARAN", "Karan Malhotra", "Product Growth Architect", "Nexus_Koramangala_Mall", "Product Strategy", "Builds self-serve onboarding funnels for enterprise SaaS"),

            # Guild 16: Artisanal Textiles, Brewing & Pop Culture (Gandhi Bazaar & Indiranagar)
            ("CHETANA", "Chetana Shenoy", "Karnataka Silk Handloom Curator", "Gandhi_Bazaar_Heritage", "Artisanal Heritage", "Preserves authentic Mysore silk weaving techniques in modern fashion"),
            ("SHIVA", "Shivashankar", "Master Brewer @ Toit & Windmills", "Indiranagar_100ft_Startups", "Culinary Arts", "Brews craft Belgian Witbier using natural cardamom and orange peel"),
            ("MEENAKSHI", "Meenakshi Sundaram", "Carnatic Music Digitization Lead", "Gandhi_Bazaar_Heritage", "Cultural Heritage", "Preserves historic veena and mridangam acoustic master tapes"),
            ("VIPUL", "Vipul Mittal", "Indie Game Developer & Pixel Artist", "Church_Street_Cafes", "Creative Arts", "Develops retro cyberpunk isometric adventure games set in Bengaluru"),
            ("GAYATRI", "Gayatri Prabhu", "South Indian Coffee Chronicler", "Church_Street_Cafes", "Culinary Heritage", "Authors books on Chikmagalur coffee bean traditions and roasting styles"),

            # Guild 17: Aviation, Terminal Logistics & Kempegowda Airport Gateways (BLR Airport)
            ("CAPT_ROY", "Capt. Sandeep Roy", "Senior Boeing 787 Captain", "Kempegowda_Airport_BLR", "Aviation Operations", "Commands long-haul flights connecting BLR to London Heathrow & SFO"),
            ("MADHAV", "Madhav Shenoy", "BLR Terminal 2 Robotics Lead", "Kempegowda_Airport_BLR", "Aviation Operations", "Supervises autonomous baggage handling and facial recognition e-gates"),
            ("TRISHA", "Trisha Sen", "Air Traffic Radar Supervisor", "Kempegowda_Airport_BLR", "Aviation Operations", "Coordinates radar separations for 700+ daily air traffic movements"),
            ("RAGHAV", "Raghavendra Bhat", "Air Cargo Customs Superintendent", "Kempegowda_Airport_BLR", "Aviation Logistics", "Clears high-value semiconductor and pharmaceutical air shipments"),
            ("NEELAM", "Neelam Joshi", "Aviation VIP Hospitality Director", "Kempegowda_Airport_BLR", "Aviation Hospitality", "Oversees international executive and diplomatic lounges at T2"),

            # Guild 18: High-Performance Distributed Databases & eBPF (Manyata & Whitefield)
            ("SUDHIR", "Sudhir Murthy", "Vector Database Kernel Maintainer", "Manyata_Tech_Park", "Core Architecture", "Implements SIMD HNSW vector distance metrics in C++"),
            ("BHARATH", "Bharath Srinivasan", "Linux eBPF Tracing Architect", "Manyata_Tech_Park", "Core Architecture", "Hooks tracepoints into OS kernel ring-buffers for microsecond profiling"),
            ("ALISHA", "Alisha Fernandes", "Kafka & Event Stream Engineer", "Whitefield_ITPB", "Core Architecture", "Streams millions of real-time transactions through cluster partitions"),
            ("JITEN", "Jitendra Solanki", "Raft Consensus Protocol Dev", "Whitefield_ITPB", "Core Architecture", "Solves Byzantine fault tolerance in distributed state machines"),
            ("DIVESH", "Divesh Aggarwal", "GPU Slurm Cluster Orchestrator", "Manyata_Tech_Park", "DevOps & Infrastructure", "Manages 512-GPU training clusters with non-blocking NVLink interconnects"),

            # Guild 19: Higher Education, Academic Leadership & Robotics (IISc & RVCE)
            ("PROF_NAIDU", "Prof. C. Naidu", "Dean of Computer Science @ RVCE", "IISc_Research_Campus", "Academic Research", "Mentors next-generation embedded system and robotics engineers"),
            ("POOJA_ED", "Pooja Hegde-Rao", "Open-Source Curriculum Director", "IISc_Research_Campus", "Higher Education", "Authors interactive agent programming labs for Indian universities"),
            ("TARUN", "Tarun Saxena", "Reinforcement Learning Fellow", "IISc_Research_Campus", "Academic Research", "Trains quadrupeds to navigate uneven terrain using PPO algorithms"),
            ("SHILPA", "Shilpa Shetty", "Student Robotics Lead @ PES", "IISc_Research_Campus", "Robotics R&D", "Builds solar-powered autonomous lawnmowers and inspection rovers"),
            ("AJAY", "Ajay Bharadwaj", "UAV Autonomous Flight Engineer", "IISc_Research_Campus", "Robotics R&D", "Tests obstacle avoidance algorithms for urban delivery drones"),

            # Guild 20: Namma Radio 91.1 FM, Podcasting & Pop Culture (Church Street)
            ("RJ_DISHA", "RJ Disha", "Host @ Namma Radio 91.1 FM", "Church_Street_Cafes", "Media & Press", "Broadcasts morning humor, Bangalore traffic updates, and coding memes"),
            ("RJ_RAAJ", "RJ Raaj", "Evening Drive Show Host @ 91.1 FM", "Church_Street_Cafes", "Media & Press", "Entertains Silk Board commuters with retro Kannada rock and city stories"),
            ("VIKAS", "Vikas Somani", "Live Audio Production Engineer", "Church_Street_Cafes", "Media & Press", "Mixes live city podcasts, jingles, and field interview feeds"),
            ("ANKITA", "Ankita Roy", "Digital Culture & Meme Strategist", "Indiranagar_100ft_Startups", "Media & Press", "Tracks viral Bangalore startup memes and tech founder lore"),
            ("HEMANT", "Hemant Sharma", "Tech Community Discord Emcee", "Church_Street_Cafes", "Media & Press", "Moderates 50,000-member Bangalore developer discussions and AMAs")
        ]

        for pid, name, role, zone, dept, bio in citizens:
            p = Persona(pid, name, role, starting_location=zone, department=dept)
            p.memory.add(f"Citizen of Bengaluru: {name}, {role} in {dept}. {bio}", importance=0.9, arousal=0.15)
            self.personas[pid] = p

    def log_event(self, pid: str, name: str, dept: str, zone: str, action: str, arousal: float):
        try:
            with self.db_lock:
                conn = sqlite3.connect(DB_PATH)
                cur = conn.cursor()
                cur.execute(
                    """INSERT INTO world_events 
                       (tick, persona_id, persona_name, department, zone, action, arousal, timestamp) 
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (self.tick_count, pid, name, dept, zone, action, arousal, time.time())
                )
                conn.commit()
                conn.close()
        except Exception:
            pass

    def log_conversation(self, conv: Dict[str, Any]):
        try:
            with self.db_lock:
                conn = sqlite3.connect(DB_PATH)
                cur = conn.cursor()
                cur.execute(
                    """INSERT INTO world_conversations 
                       (tick, world_time, zone, speaker_1, speaker_2, turn_1, turn_2, affinity, timestamp) 
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (self.tick_count, self.clock.get_time_str(), conv["zone"], conv["speaker_1"], 
                     conv["speaker_2"], conv["turn_1"], conv["turn_2"], conv["affinity"], time.time())
                )
                conn.commit()
                conn.close()
        except Exception:
            pass

    def get_recent_conversations(self, limit: int = 10) -> List[Dict[str, Any]]:
        try:
            with self.db_lock:
                conn = sqlite3.connect(DB_PATH)
                cur = conn.cursor()
                cur.execute(
                    """SELECT tick, world_time, zone, speaker_1, speaker_2, turn_1, turn_2, affinity, timestamp 
                       FROM world_conversations ORDER BY id DESC LIMIT ?""",
                    (limit,)
                )
                rows = cur.fetchall()
                conn.close()
                return [
                    {
                        "tick": r[0],
                        "world_time": r[1],
                        "zone": r[2],
                        "speaker_1": r[3],
                        "speaker_2": r[4],
                        "turn_1": r[5],
                        "turn_2": r[6],
                        "affinity": r[7],
                        "time": time.strftime("%H:%M:%S", time.localtime(r[8]))
                    }
                    for r in rows
                ]
        except Exception:
            return []

    def get_event_count(self) -> int:
        try:
            with self.db_lock:
                conn = sqlite3.connect(DB_PATH)
                cur = conn.cursor()
                cur.execute("SELECT COUNT(*) FROM world_events")
                cnt = cur.fetchone()[0]
                conn.close()
                return cnt
        except Exception:
            return 0

    def get_recent_events(self, limit: int = 30) -> List[Dict[str, Any]]:
        try:
            with self.db_lock:
                conn = sqlite3.connect(DB_PATH)
                cur = conn.cursor()
                cur.execute(
                    """SELECT tick, persona_id, persona_name, department, zone, action, arousal, timestamp 
                       FROM world_events ORDER BY id DESC LIMIT ?""",
                    (limit,)
                )
                rows = cur.fetchall()
                conn.close()
                return [
                    {
                        "tick": r[0],
                        "persona_id": r[1],
                        "name": r[2] or r[1],
                        "department": r[3] or "General",
                        "zone": r[4],
                        "action": r[5],
                        "arousal": round(r[6], 2),
                        "time": time.strftime("%H:%M:%S", time.localtime(r[7]))
                    }
                    for r in rows
                ]
        except Exception:
            return []

    def broadcast_executive_directive(self, directive_text: str) -> Dict[str, Any]:
        """Governor Lalith broadcasts a city-wide directive to all 100 Bengaluru citizens."""
        for p in self.personas.values():
            p.perceive(f"GOVERNOR DECREE from Lalith: '{directive_text}'", stress_impact=0.30)
            p.known_rumors.append(f"Governor Lalith ordered: {directive_text[:35]}")
            p.set_speech_bubble(f"Alert: {directive_text[:30]}")
        self.log_event("GOVERNOR", "Lalith (City Governor)", "City Administration", "All_Bengaluru", f"[BROADCAST] {directive_text}", 0.5)
        self.event_bus.publish("governor_directive", {
            "directive": directive_text,
            "affected_citizens": len(self.personas),
            "tick": self.tick_count
        })
        return {"status": "broadcast_sent", "directive": directive_text, "affected_citizens": len(self.personas)}

    def direct_message_citizen(self, persona_id: str, message: str) -> Dict[str, Any]:
        p = self.personas.get(persona_id.upper())
        if not p:
            return {"status": "error", "message": f"Citizen {persona_id} not found"}
        
        reply = p.chat_with_creator(message)
        self.log_event("GOVERNOR", "Lalith (City Governor)", "City Administration", p.location, f"To {p.name}: {message}", 0.2)
        self.log_event(p.id, p.name, p.department, p.location, f"To Governor Lalith: {reply}", p.current_arousal)
        return {
            "status": "success",
            "persona_id": p.id,
            "persona_name": p.name,
            "user_message": message,
            "persona_reply": reply,
            "zone": p.location,
            "wallet": p.wallet_inr,
            "energy": p.energy
        }

    def trigger_macro_event(self, event_type: str) -> Dict[str, Any]:
        """Quick Governor Macro Action triggers across Bengaluru."""
        if event_type == "MONSOON_FLOOD":
            desc = "Sudden Monsoonal Cloudburst Floods Silk Board & ORR"
            self.silk_board_congestion = 98
            self.weather = {
                "temp": "19°C", "condition": "Severe Monsoon Torrent", 
                "humidity": "95%", "aqi": 25, "desc": "Silk Board flyover underpass waterlogged, Namma Metro running at max capacity"
            }
            impact = 0.45
        elif event_type == "HACKATHON_50CR":
            desc = "₹50 Crore National AI & Agent Hackathon Inaugurated at KTPO Whitefield"
            impact = -0.15
            for p in self.personas.values():
                if "Startups" in p.location or "Tech_Park" in p.location or "Whitefield" in p.location:
                    p.earn_inr(5000.0, "Hackathon participation bounty")
        elif event_type == "POWER_GRID_DROP":
            desc = "BESCOM Substation Voltage Fluctuation at Electronic City Phase 1"
            impact = 0.40
        elif event_type == "FILTER_COFFEE_DAY":
            desc = "Free Filter Coffee Day across Gandhi Bazaar & Church Street Cafes"
            impact = -0.25
            for p in self.personas.values():
                p.adjust_energy(25.0)
                p.spend_inr(0.0, "Complimentary Chikmagalur filter coffee")
        elif event_type == "AIRPORT_METRO_EXPRESS":
            desc = "Airport Blue Line Express Inauguration: 28-Minute Transit from Majestic to BLR Airport"
            impact = -0.20
            self.silk_board_congestion = max(35, self.silk_board_congestion - 25)
        else:
            desc = f"Custom Macro Alert: {event_type}"
            impact = 0.20

        for p in self.personas.values():
            p.perceive(f"MACRO ALERT: {desc}", stress_impact=impact)
            p.known_rumors.append(desc[:40])

        self.log_event("MACRO_EVENT", "Bengaluru City Ops", "Emergency Operations", "All_Bengaluru", desc, 0.4)
        self.event_bus.publish("macro_event", {
            "event_type": event_type,
            "description": desc,
            "impact": impact,
            "tick": self.tick_count
        })
        return {"status": "triggered", "event": desc}

    def _update_stock_market(self):
        """Simulates the BLR-TECH-30 Stock Market fluctuations with Ornstein-Uhlenbeck mean-reversion."""
        theta = 0.08   # Rate of mean reversion toward fundamental anchor
        sigma = 0.025  # Gaussian volatility scale
        for stock in self.stocks:
            sym = stock["symbol"]
            base = BASE_STOCK_PRICES.get(sym, stock["price"])
            cur = stock["price"]
            # Discrete Ornstein-Uhlenbeck: drift pull + Brownian shock
            drift = theta * ((base - cur) / base)
            shock = random.gauss(0.0, sigma)
            step_pct = max(-0.06, min(0.06, drift + shock))
            new_price = max(1.0, round(cur * (1.0 + step_pct), 1))
            delta_pct = round(((new_price - cur) / max(0.1, cur)) * 100.0, 1)
            stock["price"] = new_price
            sign = "+" if delta_pct >= 0 else ""
            stock["change"] = f"{sign}{delta_pct}%"

        # Random citizen stock dividend or equity grant
        if self.personas:
            sample_size = min(3, len(self.personas))
            lucky_citizens = random.sample(list(self.personas.values()), sample_size)
            for p in lucky_citizens:
                if p.location in ["UB_City_Luxury_Towers", "Indiranagar_100ft_Startups", "Manyata_Tech_Park"]:
                    p.earn_inr(1250.0, "BLR-TECH-30 equity dividend distribution")

    def _update_weather_and_traffic(self):
        """Simulates authentic Bengaluru circadian weather shifts and Silk Board bottleneck traffic."""
        hour = self.clock.hour
        # Silk board congestion: peak rush at morning & evening; empty late night
        if 8 <= hour <= 11 or 17 <= hour <= 20:
            self.silk_board_congestion = random.randint(84, 98)
        elif 0 <= hour <= 5:
            self.silk_board_congestion = random.randint(8, 22)
        elif 12 <= hour <= 16:
            self.silk_board_congestion = random.randint(55, 75)
        else:
            self.silk_board_congestion = random.randint(40, 68)

        # Authentic Bengaluru Circadian Weather Engine
        if 0 <= hour < 4:
            temp = random.randint(15, 17)
            self.weather = {
                "temp": f"{temp}°C",
                "condition": "Midnight Starlit Chill",
                "humidity": f"{random.randint(75, 84)}%",
                "aqi": random.randint(28, 38),
                "desc": "Quiet night breeze sweeping across Outer Ring Road; street dogs resting by chai stalls",
                "phase": "MIDNIGHT",
                "icon": "🌙"
            }
        elif 4 <= hour < 7:
            temp = random.randint(16, 18)
            self.weather = {
                "temp": f"{temp}°C",
                "condition": "Early Morning Dew & Mist",
                "humidity": f"{random.randint(80, 90)}%",
                "aqi": random.randint(35, 45),
                "desc": "Cool dewy dawn over Lalbagh & Cubbon Park; Vidyarthi Bhavan chicory coffee roasting",
                "phase": "EARLY_MORNING",
                "icon": "🌅"
            }
        elif 7 <= hour < 12:
            temp = random.randint(22, 25)
            self.weather = {
                "temp": f"{temp}°C",
                "condition": "Pleasant Morning Sunshine",
                "humidity": f"{random.randint(52, 62)}%",
                "aqi": random.randint(48, 62),
                "desc": "Iconic pleasant Bangalore sunshine through banyan canopy; brisk Namma Metro rush",
                "phase": "MORNING",
                "icon": "☀️"
            }
        elif 12 <= hour < 16:
            temp = random.randint(28, 31)
            self.weather = {
                "temp": f"{temp}°C",
                "condition": "Warm Afternoon Sun",
                "humidity": f"{random.randint(45, 55)}%",
                "aqi": random.randint(62, 75),
                "desc": "Solar heat radiating from tech park asphalt; buzzing AC cooling towers at Manyata & E-City",
                "phase": "AFTERNOON",
                "icon": "🥪"
            }
        elif 16 <= hour < 18:
            temp = random.randint(23, 26)
            self.weather = {
                "temp": f"{temp}°C",
                "condition": "Afternoon Overcast & Petrichor Drizzle",
                "humidity": f"{random.randint(75, 86)}%",
                "aqi": random.randint(32, 44),
                "desc": "Sudden refreshing petrichor rain clouds cooling Indiranagar 100ft road and Silk Board",
                "phase": "LATE_AFTERNOON",
                "icon": "🌧️"
            }
        elif 18 <= hour < 21:
            temp = random.randint(21, 23)
            self.weather = {
                "temp": f"{temp}°C",
                "condition": "Amber Twilight & Evening Breeze",
                "humidity": f"{random.randint(64, 72)}%",
                "aqi": random.randint(42, 54),
                "desc": "Amber golden hour sunset fading into twilight; Church Street cafe terraces bustling",
                "phase": "EVENING",
                "icon": "🌆"
            }
        else:
            temp = random.randint(18, 20)
            self.weather = {
                "temp": f"{temp}°C",
                "condition": "Cool Starlit Night Breeze",
                "humidity": f"{random.randint(68, 76)}%",
                "aqi": random.randint(36, 46),
                "desc": "Crisp night air; Koramangala craft microbreweries, rooftop music, and late-night coding",
                "phase": "NIGHT",
                "icon": "🍺"
            }

    def set_world_time(self, hour: int, minute: int = 0) -> Dict[str, Any]:
        """Governor command to shift city time instantly to any hour."""
        self.clock.set_time(hour, minute)
        self._update_weather_and_traffic()
        return {
            "hour": self.clock.hour,
            "minute": self.clock.minute,
            "time_str": self.clock.get_time_str(),
            "time_fraction": self.clock.get_time_of_day_fraction(),
            "circadian_phase": self.clock.get_circadian_phase(),
            "circadian_phase_category": self.clock.get_circadian_phase_category(),
            "weather": self.weather,
            "silk_board_congestion": self.silk_board_congestion
        }

    def _broadcast_namma_radio(self):
        """Autonomous Namma Radio 91.1 FM Broadcasts with RJ Disha and RJ Raaj."""
        if self.tick_count % 2 != 0:
            return

        rj = random.choice(["RJ Disha", "RJ Raaj"])
        lines = [
            f"⚡ [Namma Radio 91.1 FM] {rj} live! Silk Board flyover congestion is sitting at {self.silk_board_congestion}%. If you are in an auto, make peace with your compiler or switch to Namma Metro!",
            f"☕ [Namma Radio 91.1 FM] {rj} here! Bengaluru temperature is a crisp {self.weather['temp']}. Vidyarthi Bhavan crispy benne dosas are flying off the tawa in Gandhi Bazaar!",
            f"🚀 [Namma Radio 91.1 FM] {rj} alert! BLR-TECH-30 index is buzzing! AI Startups along 100ft Road Indiranagar just announced a record sprint demo. Keep building Bengaluru!",
            f"✈️ [Namma Radio 91.1 FM] {rj} transit check: Kempegowda Airport Blue Line feeder buses are moving smoothly. Air quality index is {self.weather['aqi']} — iconic Bangalore weather!"
        ]
        chosen = random.choice(lines)
        broadcast_entry = {
            "tick": self.tick_count,
            "rj": rj,
            "time": self.clock.get_time_str(),
            "message": chosen
        }
        self.radio_broadcasts.insert(0, broadcast_entry)
        if len(self.radio_broadcasts) > 10:
            self.radio_broadcasts.pop()

    def _publish_chronicle_newspaper(self, tick_summary: List[Dict[str, Any]], stressor: Optional[str]):
        """The Bengaluru Chronicle Newsroom publishes an automated city edition."""
        if self.tick_count % 3 != 0:
            return

        timestamp = time.strftime("%Y-%m-%d %H:%M")
        wallets = [p.wallet_inr for p in self.personas.values()]
        gdp = int(sum(wallets))

        headline = stressor or f"Bengaluru City GDP Crosses ₹{gdp:,} as 100 Citizens Drive Peak Innovation"
        top_events = [f"• {p['name']} ({p['zone'].replace('_', ' ')}): {p['action']}" for p in tick_summary[:5]]

        chronicle_entry = {
            "edition": f"Vol. {self.tick_count} • {self.clock.get_time_str()}",
            "editor": "Rhea Kapoor (Senior Tech Editor)",
            "headline": headline,
            "timestamp": timestamp,
            "gdp_figure": f"₹{gdp:,}",
            "circadian_phase": self.clock.get_circadian_phase(),
            "lead_story": (
                f"Bengaluru citizens are actively navigating {self.clock.get_circadian_phase()}. "
                f"City economic activity generated ₹{gdp:,} in circulation. Weather is {self.weather['temp']} ({self.weather['condition']}). "
                f"Silk Board congestion index stands at {self.silk_board_congestion}%."
            ),
            "top_bullets": top_events
        }

        self.chronicle_headlines.insert(0, chronicle_entry)
        if len(self.chronicle_headlines) > 10:
            self.chronicle_headlines.pop()

        try:
            fpath = os.path.join(WORKSPACE_DIR, "bengaluru_chronicle_tabloid.md")
            with open(fpath, "w") as f:
                f.write("# 📰 THE BENGALURU CHRONICLE — " + str(chronicle_entry["edition"]) + "\n")
                f.write("**Editor-in-Chief:** Rhea Kapoor | **City Phase:** " + str(chronicle_entry["circadian_phase"]) + "\n\n")
                f.write("## ⚡ BREAKING: " + str(headline) + "\n\n")
                f.write(str(chronicle_entry["lead_story"]) + "\n\n")
                f.write("### 🏙️ CITY BULLETINS ACROSS 16 WARDS:\n")
                for b in top_events:
                    f.write(str(b) + "\n")
        except Exception:
            pass

    def _conduct_civic_voting(self):
        """Simulates municipal voting on active city bills with voter de-duplication and policy enactment."""
        if self.tick_count % 4 != 0:
            return

        active_bills = [b for b in self.city_bills if b["status"] == "VOTING"]
        if not active_bills:
            return

        bill = random.choice(active_bills)
        voted_set = self.bill_voter_ids.setdefault(bill["id"], set())
        available_voters = [v for v in self.personas.values() if v.id not in voted_set]
        
        if not available_voters:
            # If all citizens voted, tally final result
            if bill["yes_votes"] >= 60:
                bill["status"] = "PASSED"
            else:
                bill["status"] = "REJECTED"
            return

        sample_size = min(12, len(available_voters))
        voters = random.sample(available_voters, sample_size)
        for v in voters:
            voted_set.add(v.id)
            vote_yes = random.random() < 0.75
            if vote_yes:
                bill["yes_votes"] += 1
                v.perceive(f"Voted YES on {bill['title']}", stress_impact=-0.02)
            else:
                bill["no_votes"] += 1
                v.perceive(f"Voted NO on {bill['title']}", stress_impact=0.01)

        if bill["yes_votes"] >= 65 and bill["status"] == "VOTING":
            bill["status"] = "PASSED"
            self.log_event("COUNCIL", "City Council", "Governance", "Vidhana_Soudha_Capitol", f"[ENACTED] {bill['title']}", 0.3)
            # Tangible policy enactment
            if bill["id"] == "BILL_101":
                self.silk_board_congestion = max(15, self.silk_board_congestion - 20)
            elif bill["id"] == "BILL_102":
                self.silk_board_congestion = max(10, self.silk_board_congestion - 30)
            elif bill["id"] == "BILL_103":
                self.life_economy.macro_gdp["city_treasury_inr"] += 250000.0

    def _step_single_citizen(self, p: Persona, stressor_event: Optional[str], index: int) -> Dict[str, Any]:
        # Spatial movement (Namma Metro commute)
        moved = False
        if random.random() < 0.20:
            p.location = random.choice(BENGALURU_ZONES)
            moved = True
            p.spend_inr(35.0, f"Namma Metro commute to {p.location.replace('_', ' ')}")

        # Circadian sleep and restorative energy replenishment
        phase_cat = self.clock.get_circadian_phase_category()
        if phase_cat == "MIDNIGHT" and not getattr(p, "is_night_shift", False):
            p.adjust_energy(10.0)
            if random.random() < 0.25 and p.location != "HSR_Layout_Residences":
                p.location = "HSR_Layout_Residences"
        elif p.location in ["Cubbon_Park_Canopy", "HSR_Layout_Residences"]:
            p.adjust_energy(6.0)

        # Dual-Speed PIANO Execution (Sector-targeted novelty to eliminate thundering herd)
        world_context = (
            f"Bengaluru Time: {self.clock.get_time_str()} ({self.clock.get_circadian_phase()}). "
            f"Location: {p.location} ({ZONE_METADATA.get(p.location, {}).get('desc', '')}). "
            f"Weather: {self.weather['temp']} {self.weather['condition']}. "
            f"City Status: {stressor_event or 'Normal Bangalore traffic and clear skies'}."
        )
        is_novel = moved or (bool(stressor_event) and (p.location in (stressor_event or "") or random.random() < 0.12))
        action_desc = p.decide_dual_speed_action(world_context, is_novel=is_novel, seed=index)

        # Tech Park earnings
        if "Tech_Park" in p.location or "Startups" in p.location or "ITPB" in p.location:
            if random.random() < 0.25:
                bounty = round(random.uniform(800, 3000), 0)
                p.earn_inr(bounty, f"Completed sprint milestone at {p.location}")

        # Computer skills execution
        lower_d = action_desc.lower()
        if "browser" in lower_d or "read" in lower_d:
            with self.x11_lock:
                self.computer.launch_browser("https://news.ycombinator.com")
            action_desc = f"{action_desc} [Firefox Active]"
        elif "server" in lower_d or "uptime" in lower_d:
            res = self.computer.execute_bash("uptime")
            action_desc = f"{action_desc} [{res[1].strip()[:24]}]"
        elif "process" in lower_d or "security" in lower_d:
            res = self.computer.execute_bash("ps aux | wc -l")
            action_desc = f"{action_desc} [{res[1].strip()} procs checked]"

        p.log_computer_action(action_desc)
        p.perceive(f"Executed at {p.location}: {action_desc}", stress_impact=-0.02)

        # 1. Stanford Smallville Associative Memory Stream & Reflection
        if not hasattr(p, "associative_memory"):
            p.associative_memory = AssociativeMemoryStream(p.id, p.name)
            p.voxel_built_count = 0
        p.associative_memory.add_memory(action_desc, node_type="event", current_tick=self.tick_count)
        if p.associative_memory.should_reflect():
            refl = p.associative_memory.execute_reflection(self.tick_count)
            if refl:
                action_desc = f"{action_desc} • [Reflection: {refl['insight'][:35]}...]"

        # 2. Environmental Statefulness: Minecraft / Project Sid Voxel Construction
        if random.random() < 0.22:
            build_options = {
                "Manyata_Tech_Park": "server_rack",
                "Bagmane_Tech_Park": "quantum_datacenter_pod",
                "Whitefield_ITPB": "rooftop_solar_grid",
                "Electronic_City_Phase_1": "fiber_conduit",
                "Silk_Board_Junction": "silk_board_congestion_relief",
                "Indiranagar_100ft_Startups": "indiranagar_cafe_pod",
                "Majestic_Metro_Interchange": "metro_flyover_extension",
                "Vidhana_Soudha_Capitol": "ev_charging_station",
                "Cubbon_Park_Canopy": "tree_canopy"
            }
            chosen_structure = build_options.get(p.location, "solar_panel")
            gx = random.randint(2, 28)
            gy = random.randint(2, 28)
            if chosen_structure in BLUEPRINTS:
                placed = self.voxel_world.construct_blueprint(p.id, p.name, p.location, gx, gy, chosen_structure, self.tick_count)
                if placed:
                    p.earn_inr(4500.0, f"Constructed {chosen_structure.replace('_', ' ')} blueprint")
                    p.voxel_built_count += len(placed)
                    action_desc = f"{action_desc} 🔨 [Built {chosen_structure}]"
            else:
                self.voxel_world.place_block(p.id, p.name, p.location, gx, gy, chosen_structure, self.tick_count)
                p.earn_inr(1200.0, f"Placed {chosen_structure} infrastructure")
                p.voxel_built_count += 1
                action_desc = f"{action_desc} 🧱 [Placed {chosen_structure} ({gx},{gy})]"

        # 3. Project Sid Decentralized P2P Contract Market
        if random.random() < 0.12:
            open_bounties = self.p2p_market.get_open_bounties()
            if open_bounties and random.random() < 0.7:
                target_b = random.choice(open_bounties)
                res = self.p2p_market.claim_and_complete_bounty(target_b["id"], p.id, p.name, self.tick_count)
                if res:
                    p.earn_inr(res["reward_inr"], f"P2P Bounty: {res['title']}")
                    action_desc = f"{action_desc} 💼 [Bounty ₹{int(res['reward_inr'])}: {res['title'][:20]}]"
            elif p.wallet_inr > 20000:
                b_titles = [
                    ("Optimize Postgres WAL checkpoints", 3500.0, "DB"),
                    ("Construct 4 solar panels at tech park", 4000.0, "Infra"),
                    ("Audit Silk Board transit IoT stream", 2800.0, "Traffic"),
                    ("Deploy ArXiv multi-agent scout service", 5000.0, "AI")
                ]
                bt, rew, cat = random.choice(b_titles)
                p.spend_inr(rew, f"Posted bounty '{bt}'")
                self.p2p_market.post_bounty(p.id, p.name, bt, rew, cat, p.location, self.tick_count)

        loc = p.location
        phase_cat = self.clock.get_circadian_phase_category()

        if phase_cat == "MIDNIGHT":
            # 00:00 - 04:00: Midnight Stargazing & Late-Night Coding or Deep Sleep
            if any(w in p.department.lower() or w in p.role.lower() for w in ["architecture", "kernel", "devops", "systems", "hardware", "research"]):
                activity_state = "LATE_NIGHT_HACKING"
                venue_name = f"{loc.replace('_', ' ')} • Server Lab Terminal"
                action_desc = f"{action_desc} • 🌙 [Midnight SIMD Kernel Debugging]"
            else:
                activity_state = "RESTING_SLEEP"
                venue_name = f"{loc.replace('_', ' ')} • Co-Living Sleep Pod"
                action_desc = f"{action_desc} • 💤 [Deep Circadian Sleep & Recovery]"
        elif phase_cat == "EARLY_MORNING":
            # 04:00 - 07:00: Early Morning Dawn, Dew & Morning Jog
            if any(w in p.department.lower() or w in p.role.lower() for w in ["fitness", "sports", "wellness"]):
                activity_state = "DAWN_JOGGING"
                venue_name = "Cubbon Park Canopy • Dawn Jogging Track"
                action_desc = f"{action_desc} • 🌅 [Dawn Warmup & Cubbon Park Run]"
            elif any(w in p.department.lower() or w in p.role.lower() for w in ["hospitality", "culinary", "barista", "chef"]):
                activity_state = "FIRST_COFFEE_BREW"
                venue_name = "Gandhi Bazaar • Filter Coffee Roaster"
                action_desc = f"{action_desc} • ☕ [Roasting Single-Estate Arabica Beans]"
            elif any(w in p.department.lower() or w in p.role.lower() for w in ["aviation", "captain", "pilot"]):
                activity_state = "PREFLIGHT_RADAR_CHECK"
                venue_name = "Kempegowda Airport • Flight Dispatch T2"
                action_desc = f"{action_desc} • ✈️ [Pre-Flight Radar Separation Review]"
            else:
                activity_state = "DAWN_MEDITATION"
                venue_name = f"{loc.replace('_', ' ')} • Dewy Balcony Garden"
                action_desc = f"{action_desc} • 🧘 [Morning Yoga & Meditation]"
        elif phase_cat == "MORNING":
            # 07:00 - 12:00: Morning Standup, Metro Commute, Office Deep Architecture
            if (index % 4) == 0:
                activity_state = "METRO_COMMUTE"
                venue_name = f"{loc.replace('_', ' ')} • Namma Metro Platform"
            elif (index % 4) == 1:
                activity_state = "DARSHINI_VISIT"
                venue_name = f"{loc.replace('_', ' ')} • Filter Coffee Counter"
            elif (index % 4) == 2:
                activity_state = "CONFERENCE_MEETING"
                venue_name = f"{loc.replace('_', ' ')} • Architecture Standup Table"
            else:
                activity_state = "OFFICE_WORK"
                venue_name = f"{loc.replace('_', ' ')} • Glass Workstation #{index % 4 + 1}"
        elif phase_cat in ["AFTERNOON", "LATE_AFTERNOON"]:
            # 12:00 - 18:00: Midday Lunch, Founder Patios, Peak Afternoon Sprints
            if (index % 4) == 0:
                activity_state = "CAFETERIA_LUNCH"
                venue_name = f"{loc.replace('_', ' ')} • Artisan Dining Terrace"
            elif (index % 4) == 1:
                activity_state = "GROUP_DISCUSSION"
                venue_name = f"{loc.replace('_', ' ')} • Founder Huddle Table"
            else:
                activity_state = "OFFICE_WORK"
                venue_name = f"{loc.replace('_', ' ')} • Deep Work Pod #{index % 4 + 1}"
        elif phase_cat == "EVENING":
            # 18:00 - 21:00: Evening Golden Hour, Gym, Pubs, MG Road Stroll
            if (index % 4) == 0:
                activity_state = "GYM_WORKOUT"
                venue_name = "HSR Cult.fit Elite Gym • Free Weights Deck"
            elif (index % 4) == 1:
                activity_state = "CRAFT_PUB_VISIT"
                venue_name = "Koramangala Microbrewery • Rooftop Taproom"
            elif (index % 4) == 2:
                activity_state = "PARK_STROLL"
                venue_name = "Cubbon Park Canopy • Fountain Promenade"
            else:
                activity_state = "BUS_COMMUTE"
                venue_name = "MG Road Boulevard • Electric Transit Terminal"
        else:
            # NIGHT: 21:00 - 24:00: Nightlife, Rooftops, Family Dinner, Ambient Music
            if (index % 3) == 0:
                activity_state = "PUB_PARTY"
                venue_name = f"{loc.replace('_', ' ')} • Craft Beer Tap #{index % 4 + 1}"
            elif (index % 3) == 1:
                activity_state = "FAMILY_DINNER"
                venue_name = f"{loc.replace('_', ' ')} • Dining Room Table"
            else:
                activity_state = "LATE_NIGHT_HACKING"
                venue_name = f"{loc.replace('_', ' ')} • Workstation Monitor #{index % 4 + 1}"

        # 4. Bengaluru Living Life, Family, Career & Wealth Compounding Engine
        life_info = self.life_economy.step_citizen_life(p, self.tick_count, self.clock.get_circadian_phase(), self.personas)
        if life_info.get("events"):
            action_desc = f"{action_desc} • [{' | '.join(life_info['events'])}]"

        self.log_event(p.id, p.name, p.department, p.location, action_desc, p.current_arousal)

        return {
            "id": p.id,
            "name": p.name,
            "role": p.role,
            "department": p.department,
            "zone": p.location,
            "zone_category": ZONE_METADATA.get(p.location, {}).get("category", "Hub"),
            "action": action_desc,
            "activity_state": activity_state,
            "venue_name": venue_name,
            "arousal": round(p.current_arousal, 2),
            "wallet_inr": round(p.wallet_inr, 2),
            "energy": round(p.energy, 1),
            "speech_bubble": p.speech_bubble.get("text", "") if p.speech_bubble else "",
            "relationships": len(p.relationships),
            "marital_status": life_info.get("marital_status", "SINGLE"),
            "partner_name": life_info.get("partner_name"),
            "children_count": life_info.get("children_count", 0),
            "happiness": life_info.get("happiness", 75.0),
            "net_worth": life_info.get("net_worth", p.wallet_inr),
            "doublings": life_info.get("doublings", 0),
            "has_company": life_info.get("has_company", False)
        }

    def _conduct_bengaluru_conversations(self, current_context: str) -> List[Dict[str, Any]]:
        active_conversations = []
        zone_groups: Dict[str, List[Persona]] = {}
        for p in self.personas.values():
            zone_groups.setdefault(p.location, []).append(p)

        # 1. Multi-person Group Discussions (in Conference Rooms & Cafe Patios)
        GROUP_TOPICS = [
            ("Distributed POSIX shm architecture with zero-copy CRDT deltas", "Manyata Tech Park • Glass Boardroom A"),
            ("Series A valuation: ₹15 Cr at ₹75 Cr pre-money and term-sheet governance", "Indiranagar 100ft • Rooftop Venture Lounge"),
            ("Single-origin Coorg Arabica vs 80:20 chicory filter coffee blend", "Church Street Cafes • Patio Table #2"),
            ("Kubernetes multi-region failover when Silk Board fiber link hiccups", "Electronic City • Edge Systems Lab"),
            ("Municipal Bill #104: EV charging mandates across Outer Ring Road", "Vidhana Soudha • Committee Room 4"),
            ("Authentic Benne Masala Dosa crispness and ghee temperature control", "Gandhi Bazaar • Heritage Coffee Corner"),
            ("Zero-trust API gateway latency optimization with eBPF probes", "Whitefield ITPB • Microservices Hub"),
            ("Craft brewery dry-hop aroma and Belgian Wit vs New England IPA profiles", "Koramangala Brewery & Pub • Rooftop Taproom"),
            ("High-intensity interval training vs 5x5 compound Olympic barbell presses", "HSR Cult.fit Elite Gym • Free Weights Deck"),
            ("Cubbon Park morning jogging routine and bird-watching canopy conservation", "Cubbon Park Canopy • Botanical Fountain Plaza"),
            ("BMTC Volvo Route 335-E scheduling vs Outer Ring Road metro feeder frequency", "MG Road Boulevard • Electric Transit Terminal"),
            ("Angel investing portfolio: Doubling net worth in Bangalore AI startups & SaaS equity", "Indiranagar 100ft • Rooftop Venture Lounge"),
            ("Vidhana Soudha wedding planning, engagement rings, and setting up an HSR household", "Church Street Cafes • Corner Lounge"),
            ("Welcoming a newborn, toddler milestones, and securing National Public School admission", "Cubbon Park Canopy • Shaded Family Pavilion"),
            ("Weekend road trip up Nandi Hills peak for sunrise and skyline cocktails at UB City", "UB City Luxury Towers • Skyline Observation Deck"),
            ("Bengaluru Macro-GDP surging past ₹4,200 Crores at +9.4% annual growth rate", "Manyata Tech Park • Executive Suite"),
            ("Testing DevPulse AI eBPF profiler flamegraphs and kernel trace overhead", "Manyata Tech Park • Glass Boardroom A"),
            ("Single-estate Coorg micro-lot anaerobic natural coffee aroma notes", "Church Street Cafes • Corner Lounge"),
            ("Aura Titanium Smart Band continuous Vo2Max and HRV recovery stats", "HSR Cult.fit Elite Gym • Free Weights Deck")
        ]

        for zone, occupants in zone_groups.items():
            if len(occupants) >= 3 and random.random() < 0.75:
                members = random.sample(occupants, min(4, len(occupants)))
                topic, venue = random.choice(GROUP_TOPICS)
                speaker_1, speaker_2, speaker_3 = members[0], members[1], members[2]
                speaker_4 = members[3] if len(members) >= 4 else None

                t1 = f"Look at the benchmark on {topic.lower()}. We need to lock the design."
                t2 = "I reviewed the numbers. If we decouple the control plane, latency drops by 60%."
                t3 = "Agreed. Let's run a canary test before the afternoon sync."
                t4 = "I will verify the telemetry in our dashboard right now."

                group_conv = {
                    "id": int(time.time() * 1000) % 1000000,
                    "tick": self.tick_count,
                    "world_time": self.clock.get_time_str(),
                    "zone": zone,
                    "venue": venue,
                    "is_group": True,
                    "participants": [m.name for m in members],
                    "speaker_1": speaker_1.name,
                    "speaker_2": speaker_2.name,
                    "speaker_3": speaker_3.name,
                    "speaker_4": speaker_4.name if speaker_4 else None,
                    "turn_1": t1,
                    "turn_2": t2,
                    "turn_3": t3,
                    "turn_4": t4 if speaker_4 else None,
                    "affinity": round(random.uniform(0.75, 0.95), 2),
                    "topic": topic
                }
                self.log_conversation(group_conv)
                active_conversations.append(group_conv)
                speaker_1.set_speech_bubble(t1)
                speaker_2.set_speech_bubble(t2)

        # 2. Pairwise Spoken Dialogues
        pairs = []
        for zone, occupants in zone_groups.items():
            if len(occupants) >= 2 and random.random() < 0.60:
                p1, p2 = random.sample(occupants, 2)
                pairs.append((p1, p2, zone))

        if pairs:
            # Parallel dialogues (max 8 simultaneous conversations)
            with concurrent.futures.ThreadPoolExecutor(max_workers=min(8, len(pairs))) as ex:
                futs = [ex.submit(p1.converse_with, p2, z, current_context) for p1, p2, z in pairs[:8]]
                for f in futs:
                    res = f.result()
                    if res:
                        self.log_conversation(res)
                        active_conversations.append(res)
                        # Project Sid: Mutate persistent bilateral social graph
                        s1 = res.get("speaker_1", "")
                        s2 = res.get("speaker_2", "")
                        if s1 and s2:
                            self.social_graph.record_interaction(
                                s1, s2, self.tick_count,
                                trust_delta=0.08,
                                familiarity_delta=6,
                                notes=f"Spoke in {res.get('zone', 'Bengaluru')}"
                            )

        return active_conversations

    def step(self) -> Dict[str, Any]:
        self.tick_count += 1
        self.clock.advance(minutes=15)

        # 1. Update Market, Weather, Traffic, Radio
        self._update_stock_market()
        self._update_weather_and_traffic()
        self._broadcast_namma_radio()

        # Realistic Environmental City Stressors
        stressor_event = None
        if random.random() < 0.35:
            stressors = [
                (f"Heavy Traffic Bottleneck at Silk Board (Congestion: {self.silk_board_congestion}%)", 0.40),
                ("Namma Metro Purple Line Signal Modernization at Majestic Hub", 0.20),
                (f"Pre-Monsoon Shower across Indiranagar & Koramangala ({self.weather['temp']})", 0.25),
                ("Substation Voltage Fluctuation at Manyata Tech Park Phase 2", 0.35),
                ("Tech Unicorn IPO Listing Celebration on UB City 14th Floor", 0.15),
                ("Kempegowda Airport Runway Visibility Advisory (Morning Fog)", 0.25)
            ]
            s_name, s_impact = random.choice(stressors)
            stressor_event = s_name
            targets = random.sample(list(self.personas.values()), 8)
            for target_p in targets:
                target_p.perceive(f"CITY ALERT: {s_name}", s_impact)
                target_p.known_rumors.append(s_name)
                target_p.onsets.append(round(random.uniform(1.2, 4.2), 2))

        # 2. Step ALL 100 Citizens Simultaneously in Parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=60) as executor:
            futs = [
                executor.submit(self._step_single_citizen, p, stressor_event, i) 
                for i, p in enumerate(self.personas.values())
            ]
            tick_summary = [f.result() for f in futs]

        # 3. Spoken Dialogues Across Bengaluru
        current_ctx = (
            f"Bengaluru {self.clock.get_time_str()} ({self.clock.get_circadian_phase()}). "
            f"Weather: {self.weather['temp']} {self.weather['condition']}. Status: {stressor_event or 'Smooth transit and sunny skies'}."
        )
        conversations = self._conduct_bengaluru_conversations(current_ctx)
        self.last_conversations = conversations

        # 4. Publish The Bengaluru Chronicle Newspaper
        self._publish_chronicle_newspaper(tick_summary, stressor_event)

        # 5. Civic Voting on City Bills
        self._conduct_civic_voting()

        # 6. Capture Virtual Actuator Desktop
        with self.x11_lock:
            self.computer.capture_screenshot("/Users/lalith/ray_agent_world/static/live_screen.png")

        # 7. Step Real-World Macro-GDP & Economic Accounting Engine (GDP = C + I + G + NX)
        macro_econ = self.life_economy.step_macro_economy(self.personas, self.tick_count)

        # 8. Step Synthetic Consumer Marketing & Diffusion Engine (Bass Diffusion + Wallet Test)
        marketing_res = self.consumer_marketing.step_marketing_diffusion(self.personas, self.tick_count, macro_econ)
        marketing_analytics = self.consumer_marketing.get_campaign_analytics()

        # 9. Real-Time Data Harvester Sync
        real_intel = self.realtime_harvester.get_intel()
        if real_intel and "weather" in real_intel:
            rw = real_intel["weather"]
            if self.weather.get("temp") and rw.get("temperature_c"):
                self.weather["real_bangalore_temp"] = f"{rw['temperature_c']}°C"
                self.weather["real_windspeed"] = f"{rw.get('windspeed_kmh', 10)} km/h"

        # 10. Step Bengaluru Live Broadcast TV Network (3 Channels)
        recent_fg = None
        try:
            with sqlite3.connect(DB_PATH) as conn:
                r = conn.execute("SELECT summary_json FROM consumer_focus_groups ORDER BY id DESC LIMIT 1").fetchone()
                if r:
                    recent_fg = {"summary": json.loads(r[0])}
        except Exception:
            pass

        self.tv_network.update_broadcast(
            world_time=self.clock.get_time_str(),
            circadian_phase=self.clock.get_circadian_phase(),
            weather=self.weather,
            silk_congestion=self.silk_board_congestion,
            stocks=self.stocks,
            recent_fg_audit=recent_fg,
            real_intel=real_intel
        )
        tv_state = self.tv_network.get_all_channels()

        # 11. Step Metropolis Social Media ("Namma-Net" BLR Pulse & Community Groups)
        self.social_os.step(
            tick=self.tick_count,
            world_time=self.clock.get_time_str(),
            circadian_phase=self.clock.get_circadian_phase(),
            recent_fg_audit=recent_fg
        )
        social_state = self.social_os.get_social_state()

        all_arousals = [p.current_arousal for p in self.personas.values()]
        all_wallets = [p.wallet_inr for p in self.personas.values()]
        all_energies = [p.energy for p in self.personas.values()]
        all_onsets = [o for p in self.personas.values() for o in p.onsets] or [2.8]

        blr_tech_index = round(sum(s["price"] for s in self.stocks) * 1.15, 2)

        # 3. Step Lifecycle, Spatial Diffusion, Sandbox Execution, and Vector Brain
        lifecycle_res = self.lifecycle_engine.step_lifecycle(self.personas, macro_econ.get("active_startups", []), self.tick_count)
        diffusion_res = self.spatial_diffusion.step_spatial_diffusion(self.personas, self.tick_count)

        if self.tick_count % 2 == 0:
            sample_tasks = [
                ("BNT-101", "Fast AST Kernel Trace", "Aarav Sharma", "import sys\nprint('SIMD AST trace complete: 142 nodes parsed in 12μs')\nassert True\n"),
                ("BNT-102", "Namma Metro Load Balancer", "Priya Patel", "import json\nroutes = {'Purple': 'Optimal', 'Green': 'Congested'}\nprint(json.dumps(routes))\n"),
                ("BNT-103", "Silk Board Flow Predictor", "Vikram Rao", "flow_rate = 0.78 * 1400\nprint(f'Throughput: {flow_rate} veh/hr')\n")
            ]
            t_id, t_title, t_dev, t_code = sample_tasks[self.tick_count % len(sample_tasks)]
            self.sandbox_engine.execute_bounty_task(t_id, t_title, t_dev, t_code)

        for conv in conversations[:3]:
            for p in conv.get("participants", []):
                self.vector_brain.store_memory(p, p, conv.get("topic", "Bangalore Tech Architecture"), "DIALOGUE", self.tick_count)

        # Check for alerts to dispatch
        if self.silk_board_congestion >= 90:
            self.webhook_bridge.dispatch_alert("Silk Board 100% Gridlock", "Severe bottleneck on Outer Ring Road.", "ALERT")
        for ev in lifecycle_res.get("events", []):
            if ev.get("type") == "COMPANY_BANKRUPTCY":
                self.webhook_bridge.dispatch_alert("Corporate Bankruptcy Declared", ev.get("message", ""), "ALERT")

        # 4. Step Dedicated Homes, Citizen Smartphones & Urban Fauna
        is_night = self.clock.get_circadian_phase_category() in ["NIGHT", "MIDNIGHT", "EARLY_MORNING"]
        housing_state = self.housing_engine.step_circadian_residence(self.personas, self.clock.get_circadian_phase_category(), self.tick_count)
        phones_state = self.smartphone_engine.step_phones(self.personas, is_night, self.tick_count)
        fauna_state = self.fauna_engine.step_fauna(self.personas, self.tick_count)

        telemetry = {
            "city_name": os.getenv("METROPOLIS_NAME", "Bengaluru Living Metropolis OS"),
            "world_name": os.getenv("METROPOLIS_NAME", "Bengaluru Living Metropolis OS"),
            "tick": self.tick_count,
            "world_time": self.clock.get_time_str(),
            "time_fraction": self.clock.get_time_of_day_fraction(),
            "circadian_phase": self.clock.get_circadian_phase(),
            "circadian_phase_category": self.clock.get_circadian_phase_category(),
            "tv_broadcast": tv_state,
            "social_pulse": social_state,
            "real_intel": real_intel,
            "community_places": {
                "temples": ["🛕 Bull Temple (Dodda Basavana Gudi)", "🛕 Someshwara Temple Ulsoor", "🛕 ISKCON Bangalore"],
                "churches": ["⛪ St. Mark's Cathedral (MG Road)", "⛪ St. Mary's Basilica (Shivajinagar)", "⛪ Holy Trinity Church"],
                "housing": ["🏘️ Dev Co-Living PG (Indiranagar)", "🏡 HSR Layout Sector 1-7 Homes", "🏢 Manyata Cloud Pods"],
                "care_centers": ["🏥 Narayana Health Care Clinic (HSR)", "🏥 Manipal Emergency Ward", "👶 Dev Community Daycare"]
            },
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_citizens": len(self.personas),
            "active_concurrent_models": len(tick_summary),
            "execution_mode": "PIANO Dual-Speed Concurrency (System-1 Reflex + System-2 LLM)",
            "zone_coordinates": ZONE_COORDINATES,
            "zone_metadata": ZONE_METADATA,
            "metro_lines": METRO_LINES,
            "stressor": stressor_event,
            "weather": self.weather,
            "silk_board_congestion": self.silk_board_congestion,
            "stocks": self.stocks,
            "blr_tech_index": f"{blr_tech_index:,.2f}",
            "radio_broadcasts": self.radio_broadcasts[:4],
            "economy": {
                "total_gdp_inr": f"₹{int(sum(all_wallets)):,}",
                "mean_wallet_inr": f"₹{int(statistics.mean(all_wallets)):,}",
                "mean_energy": f"{round(statistics.mean(all_energies), 1)}%",
                "top_earner": max(self.personas.values(), key=lambda p: p.wallet_inr).name,
                "real_gdp_crores": f"₹{macro_econ['macro_gdp']['gdp_crores']:,.2f} Cr",
                "annual_growth_rate": f"+{macro_econ['macro_gdp']['annual_growth_rate']}% YoY",
                "consumption_c_cr": f"₹{macro_econ['macro_gdp']['consumption_c_cr']:,.2f} Cr",
                "investment_i_cr": f"₹{macro_econ['macro_gdp']['investment_i_cr']:,.2f} Cr",
                "govt_spending_g_cr": f"₹{macro_econ['macro_gdp']['govt_spending_g_cr']:,.2f} Cr",
                "net_exports_nx_cr": f"₹{macro_econ['macro_gdp']['net_exports_nx_cr']:,.2f} Cr",
                "city_treasury_cr": f"₹{macro_econ['macro_gdp']['city_treasury_inr']/10000000:,.2f} Cr"
            },
            "macro_gdp": macro_econ["macro_gdp"],
            "forbes_rich_list": macro_econ["forbes_rich_list"],
            "active_startups": macro_econ["active_startups"],
            "active_families": macro_econ["active_families"],
            "life_milestones": macro_econ["recent_milestones"],
            "metrics": {
                "mean_onset": f"{round(statistics.mean(all_onsets), 2)} min",
                "mean_arousal": f"{round(statistics.mean(all_arousals), 3)} stress_index",
                "satisfaction_NPS": round((len([a for a in all_arousals if a < 0.4]) - len([a for a in all_arousals if a > 0.7])) / len(all_arousals) * 100, 1),
                "WOM_k_factor": f"{round(random.uniform(1.3, 1.9), 2)}x",
                "event_count": self.get_event_count()
            },
            "persona_states": tick_summary,
            "citizens": tick_summary,
            "active_conversations": conversations,
            "recent_conversations": self.get_recent_conversations(limit=10),
            "recent_events": self.get_recent_events(limit=30),
            "event_bus_recent": self.event_bus.get_recent(limit=20),
            "city_bills": self.city_bills,
            "chronicle_headlines": self.chronicle_headlines[:4],
            "voxel_world": self.voxel_world.get_all_world_stats(),
            "social_bonds": self.social_graph.get_top_social_bonds(),
            "p2p_bounties": self.p2p_market.get_open_bounties(),
            "recent_contracts": self.p2p_market.get_recent_completed_contracts(),
            "marketing_intelligence": {
                "step_result": marketing_res,
                "analytics": marketing_analytics
            },
            "lifecycle_stats": self.lifecycle_engine.get_lifecycle_stats(),
            "sandbox_executions": self.sandbox_engine.get_recent_runs(),
            "spatial_diffusion": diffusion_res,
            "vector_brain_count": self.vector_brain.get_total_indexed_memories(),
            "recent_alerts": self.webhook_bridge.get_recent_alerts(),
            "housing_state": housing_state,
            "phones_state": phones_state,
            "fauna_state": fauna_state,
            "named_dogs": self.fauna_engine.dogs,
            "named_cats": self.fauna_engine.cats,
            "bengaluru_parks": self.fauna_engine.parks
        }
        return telemetry

if __name__ == "__main__":
    world = LivingWorld()
    print("Initialized 100-citizen Bengaluru Living Metropolis. Stepping tick 1...")
    t0 = time.time()
    res = world.step()
    dt = time.time() - t0
    print(f"City Tick #{res['tick']} completed in {dt:.2f}s | {res['world_time']} ({res['circadian_phase']})")
    print(f"Economy: GDP {res['economy']['total_gdp_inr']} | BLR-TECH-30 Index: {res['blr_tech_index']} | Top Earner: {res['economy']['top_earner']}")
    print(f"Citizens: {res['total_citizens']} Active across {len(res['zone_coordinates'])} Bengaluru Sectors")
    print(f"Weather: {res['weather']['temp']} {res['weather']['condition']} | Silk Board Congestion: {res['silk_board_congestion']}%")
    print(f"Spoken Dialogues: {len(res['active_conversations'])} simultaneous conversations")
