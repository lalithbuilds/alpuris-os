"""
Consumer Marketing Engine & Synthetic Focus Group Studio
Bengaluru Living Agent Metropolis OS (100 Autonomous Citizens)

Core Capabilities:
1. Consumer Persona Profiling (100 unique citizens with income, price sensitivity, brand skepticism, sector affinities).
2. Cognitive Purchase Loop ("The Wallet Test"):
   - Gate 1: Deterministic Solvency Gate (checks discretionary budget vs price).
   - Gate 2: System-2 Value & Skepticism Evaluation with Subconscious Monologue generation.
3. Omnichannel Ad Campaigns (Commute Billboards, OASIS Social Media Feeds, Radio Commercials, Tech Huddles).
4. Word-of-Mouth (WOM) Viral Loops & Bass Diffusion Modeling:
   - dN(t)/dt = [p + q * (N(t)/M)] * (M - N(t))
   - Promoters (NPS 9-10) advocate; Detractors (NPS 1-6) deter peers.
5. A/B Variant Testing Engine (Side-by-side copy, pricing, conversion, revenue, and sentiment).
6. Synthetic Focus Group Interactive Interviewer (On-demand demographic interrogation with qualitative quotes).
"""

import os
import math
import time
import json
import random
import re
import sqlite3
import threading
from typing import Dict, List, Any, Optional, Tuple

DB_PATH = "/Users/lalith/ray_agent_world/world_memory.sqlite"

SECTORS = [
    "TECH_DEV_TOOL",
    "LIFESTYLE_LUXURY",
    "BEVERAGE_FOOD",
    "HEALTH_FITNESS",
    "FINTECH_SaaS",
    "ECO_MOBILITY"
]

OBJECTIONS = [
    "PRICE_RESISTANCE",
    "BRAND_SKEPTICISM",
    "LOW_CATEGORY_RELEVANCE",
    "WEAK_AD_COPY",
    "SOLVENCY_BUFFER_BREACH"
]

class ConsumerMarketingEngine:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self.lock = threading.Lock()
        self._init_db()
        self.consumer_profiles: Dict[str, Dict[str, Any]] = {}
        self.campaigns: Dict[str, Dict[str, Any]] = {}
        self._load_or_bootstrap_state()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.cursor()
            cur.execute(
                """CREATE TABLE IF NOT EXISTS consumer_campaigns (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    tagline TEXT,
                    sector TEXT NOT NULL,
                    price_inr REAL NOT NULL,
                    claimed_utility REAL DEFAULT 7.5,
                    actual_quality REAL DEFAULT 7.5,
                    variant TEXT DEFAULT 'A',
                    channel TEXT DEFAULT 'ALL',
                    status TEXT DEFAULT 'ACTIVE',
                    created_tick INTEGER DEFAULT 0,
                    target_audience TEXT DEFAULT 'ALL',
                    impressions INTEGER DEFAULT 0,
                    clicks INTEGER DEFAULT 0,
                    purchases INTEGER DEFAULT 0,
                    revenue_inr REAL DEFAULT 0.0,
                    promoters INTEGER DEFAULT 0,
                    passives INTEGER DEFAULT 0,
                    detractors INTEGER DEFAULT 0
                )"""
            )
            cur.execute(
                """CREATE TABLE IF NOT EXISTS consumer_transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    campaign_id TEXT NOT NULL,
                    citizen_id TEXT NOT NULL,
                    citizen_name TEXT NOT NULL,
                    tick INTEGER NOT NULL,
                    price_inr REAL NOT NULL,
                    decision TEXT NOT NULL,
                    objection_reason TEXT,
                    thought_monologue TEXT NOT NULL,
                    sentiment_score REAL DEFAULT 0.0,
                    nps_rating INTEGER DEFAULT 7,
                    wom_shared INTEGER DEFAULT 0,
                    timestamp REAL NOT NULL
                )"""
            )
            cur.execute(
                """CREATE TABLE IF NOT EXISTS citizen_consumer_profiles (
                    citizen_id TEXT PRIMARY KEY,
                    citizen_name TEXT NOT NULL,
                    role TEXT NOT NULL,
                    department TEXT NOT NULL,
                    price_sensitivity REAL DEFAULT 0.5,
                    brand_skepticism REAL DEFAULT 0.5,
                    tech_affinity REAL DEFAULT 1.0,
                    lifestyle_affinity REAL DEFAULT 1.0,
                    food_beverage_affinity REAL DEFAULT 1.0,
                    fitness_affinity REAL DEFAULT 1.0,
                    fintech_affinity REAL DEFAULT 1.0,
                    mobility_affinity REAL DEFAULT 1.0,
                    discretionary_ratio REAL DEFAULT 0.25,
                    influence_weight REAL DEFAULT 1.0,
                    inventory_json TEXT DEFAULT '[]',
                    ad_memory_json TEXT DEFAULT '{}'
                )"""
            )
            cur.execute(
                """CREATE TABLE IF NOT EXISTS consumer_focus_groups (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    campaign_id TEXT,
                    question TEXT NOT NULL,
                    cohort_filter TEXT DEFAULT 'ALL',
                    tick INTEGER NOT NULL,
                    summary_json TEXT NOT NULL,
                    quotes_json TEXT NOT NULL,
                    timestamp REAL NOT NULL
                )"""
            )
            conn.commit()

    def _load_or_bootstrap_state(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            rows = cur.execute("SELECT * FROM consumer_campaigns").fetchall()
            for r in rows:
                self.campaigns[r["id"]] = dict(r)

            rows = cur.execute("SELECT * FROM citizen_consumer_profiles").fetchall()
            for r in rows:
                p = dict(r)
                p["inventory"] = json.loads(p.get("inventory_json") or "[]")
                p["ad_memory"] = json.loads(p.get("ad_memory_json") or "{}")
                self.consumer_profiles[r["citizen_id"]] = p

            # If consumer profiles are sparse, populate from citizen_life_records
            if len(self.consumer_profiles) < 50:
                life_citizens = cur.execute("SELECT citizen_id, citizen_name, career_level, salary_inr FROM citizen_life_records").fetchall()
                for c in life_citizens:
                    cid = c["citizen_id"]
                    if cid not in self.consumer_profiles:
                        c_level = c["career_level"] or 2
                        salary = c["salary_inr"] or 5000.0
                        name = c["citizen_name"]
                        
                        # Infer dept & role from career level & name
                        role = "Senior Systems Lead" if c_level >= 4 else "Mid Software Engineer" if c_level == 3 else "Associate Specialist"
                        dept = "Core Architecture" if "Aarav" in name or "Srinivasan" in name or "Murthy" in name else "Engineering"

                        price_sens = max(0.15, min(0.85, 1.0 - (salary / 25000.0)))
                        skepticism = round(random.uniform(0.40, 0.85), 2)
                        tech_aff = round(random.uniform(1.2, 2.5), 2)
                        life_aff = round(random.uniform(0.9, 2.2), 2)
                        food_aff = round(random.uniform(1.2, 2.6), 2)
                        fit_aff = round(random.uniform(0.8, 2.2), 2)

                        prof = {
                            "citizen_id": cid,
                            "citizen_name": name,
                            "role": role,
                            "department": dept,
                            "price_sensitivity": round(price_sens, 2),
                            "brand_skepticism": skepticism,
                            "tech_affinity": tech_aff,
                            "lifestyle_affinity": life_aff,
                            "food_beverage_affinity": food_aff,
                            "fitness_affinity": fit_aff,
                            "fintech_affinity": 1.2,
                            "mobility_affinity": 1.1,
                            "discretionary_ratio": 0.35 if c_level >= 4 else 0.22,
                            "influence_weight": 1.8 if c_level >= 4 else 1.0,
                            "inventory": [],
                            "ad_memory": {}
                        }
                        self.consumer_profiles[cid] = prof
                        cur.execute(
                            """INSERT OR REPLACE INTO citizen_consumer_profiles 
                               (citizen_id, citizen_name, role, department, price_sensitivity, 
                                brand_skepticism, tech_affinity, lifestyle_affinity, food_beverage_affinity, 
                                fitness_affinity, fintech_affinity, mobility_affinity, discretionary_ratio, 
                                influence_weight, inventory_json, ad_memory_json)
                               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                            (cid, name, role, dept, prof["price_sensitivity"], skepticism, tech_aff, life_aff, 
                             food_aff, fit_aff, 1.2, 1.1, prof["discretionary_ratio"], prof["influence_weight"], "[]", "{}")
                        )
                conn.commit()

        if not self.campaigns:
            self._inject_starter_campaigns()

    def _inject_starter_campaigns(self):
        starters = [
            {
                "id": "CAMP-001-A",
                "name": "DevPulse AI eBPF Profiler",
                "tagline": "Microsecond Linux kernel tracing & SIMD flamegraphs with zero runtime overhead.",
                "sector": "TECH_DEV_TOOL",
                "price_inr": 2499.0,
                "claimed_utility": 8.8,
                "actual_quality": 8.9,
                "variant": "A (Benchmark-Driven)",
                "channel": "COMMUTE_BILLBOARD",
                "target_audience": "Core Architecture, DevOps & Infrastructure",
                "status": "ACTIVE",
                "created_tick": 1
            },
            {
                "id": "CAMP-001-B",
                "name": "DevPulse AI eBPF Profiler (Pro)",
                "tagline": "Supercharge your developer superpowers! 10x debugging speed with automated AI fix prompts.",
                "sector": "TECH_DEV_TOOL",
                "price_inr": 3499.0,
                "claimed_utility": 7.5,
                "actual_quality": 7.8,
                "variant": "B (Hype / Lifestyle-Driven)",
                "channel": "OASIS_SOCIAL_FEED",
                "target_audience": "Core Architecture, DevOps & Infrastructure",
                "status": "ACTIVE",
                "created_tick": 1
            },
            {
                "id": "CAMP-002-A",
                "name": "Coorg Micro-Lot Arabica Roast",
                "tagline": "Single-estate 88+ SCA score anaerobic natural coffee beans roasted fresh in Indiranagar.",
                "sector": "BEVERAGE_FOOD",
                "price_inr": 650.0,
                "claimed_utility": 9.2,
                "actual_quality": 9.4,
                "variant": "A (Artisan Heritage)",
                "channel": "ALL",
                "target_audience": "ALL",
                "status": "ACTIVE",
                "created_tick": 1
            },
            {
                "id": "CAMP-003-A",
                "name": "Aura Titanium Smart Band",
                "tagline": "Continuous HRV recovery tracking, Vo2Max cardiac monitoring & sleep optimization.",
                "sector": "HEALTH_FITNESS",
                "price_inr": 4999.0,
                "claimed_utility": 8.0,
                "actual_quality": 8.2,
                "variant": "A (Performance Athlete)",
                "channel": "ALL",
                "target_audience": "Wellness & Health, Aviation Operations",
                "status": "ACTIVE",
                "created_tick": 1
            }
        ]

        for s in starters:
            self.create_or_update_campaign(
                campaign_id=s["id"],
                name=s["name"],
                tagline=s["tagline"],
                sector=s["sector"],
                price_inr=s["price_inr"],
                claimed_utility=s["claimed_utility"],
                actual_quality=s["actual_quality"],
                variant=s["variant"],
                channel=s["channel"],
                target_audience=s["target_audience"],
                tick=s["created_tick"]
            )

    def register_or_update_profile(self, citizen: Any) -> Dict[str, Any]:
        cid = citizen.id if hasattr(citizen, "id") else citizen.get("citizen_id", "CIT_UNK")
        if cid in self.consumer_profiles:
            return self.consumer_profiles[cid]

        role = getattr(citizen, "role", None) or citizen.get("role", "Citizen")
        dept = getattr(citizen, "department", None) or citizen.get("department", "General")
        name = getattr(citizen, "name", None) or citizen.get("citizen_name", cid)

        price_sens = 0.50
        skepticism = 0.50
        tech_aff = 1.0
        lifestyle_aff = 1.0
        food_aff = 1.0
        fitness_aff = 1.0
        fintech_aff = 1.0
        mobility_aff = 1.0
        disc_ratio = 0.25
        influence = 1.0

        if any(w in dept.lower() for w in ["architecture", "kernel", "devops", "systems", "hardware", "research"]):
            tech_aff = round(random.uniform(2.0, 2.8), 2)
            skepticism = round(random.uniform(0.70, 0.92), 2)
            price_sens = round(random.uniform(0.25, 0.45), 2)
            influence = round(random.uniform(1.2, 1.8), 2)
        elif any(w in role.lower() for w in ["founder", "ceo", "director", "partner", "lead", "architect", "captain"]):
            tech_aff = round(random.uniform(1.8, 2.4), 2)
            lifestyle_aff = round(random.uniform(1.7, 2.5), 2)
            price_sens = round(random.uniform(0.15, 0.35), 2)
            skepticism = round(random.uniform(0.45, 0.70), 2)
            disc_ratio = 0.40
            influence = round(random.uniform(1.5, 2.2), 2)
        elif any(w in dept.lower() for w in ["hospitality", "culinary", "media", "culture", "wellness"]):
            food_aff = round(random.uniform(2.2, 2.9), 2)
            lifestyle_aff = round(random.uniform(1.8, 2.5), 2)
            skepticism = round(random.uniform(0.25, 0.50), 2)
            tech_aff = round(random.uniform(0.6, 1.2), 2)
            price_sens = round(random.uniform(0.40, 0.65), 2)
            influence = round(random.uniform(1.3, 2.0), 2)
        elif any(w in dept.lower() for w in ["fitness", "sports", "wellness"]):
            fitness_aff = round(random.uniform(2.4, 3.0), 2)
            food_aff = round(random.uniform(1.5, 2.2), 2)
            price_sens = round(random.uniform(0.35, 0.55), 2)
        elif any(w in dept.lower() for w in ["finance", "banking", "legal", "audit"]):
            fintech_aff = round(random.uniform(2.0, 2.7), 2)
            skepticism = round(random.uniform(0.75, 0.95), 2)
            price_sens = round(random.uniform(0.50, 0.75), 2)

        profile = {
            "citizen_id": cid,
            "citizen_name": name,
            "role": role,
            "department": dept,
            "price_sensitivity": price_sens,
            "brand_skepticism": skepticism,
            "tech_affinity": tech_aff,
            "lifestyle_affinity": lifestyle_aff,
            "food_beverage_affinity": food_aff,
            "fitness_affinity": fitness_aff,
            "fintech_affinity": fintech_aff,
            "mobility_affinity": mobility_aff,
            "discretionary_ratio": disc_ratio,
            "influence_weight": influence,
            "inventory": [],
            "ad_memory": {}
        }

        with self.lock:
            self.consumer_profiles[cid] = profile
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """INSERT OR REPLACE INTO citizen_consumer_profiles 
                       (citizen_id, citizen_name, role, department, price_sensitivity, 
                        brand_skepticism, tech_affinity, lifestyle_affinity, food_beverage_affinity, 
                        fitness_affinity, fintech_affinity, mobility_affinity, discretionary_ratio, 
                        influence_weight, inventory_json, ad_memory_json)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (cid, name, role, dept, price_sens, skepticism, tech_aff, lifestyle_aff, 
                     food_aff, fitness_aff, fintech_aff, mobility_aff, disc_ratio, influence, "[]", "{}")
                )
                conn.commit()

        return profile

    def create_or_update_campaign(
        self,
        campaign_id: str,
        name: str,
        tagline: str,
        sector: str,
        price_inr: float,
        claimed_utility: float = 8.0,
        actual_quality: float = 8.0,
        variant: str = "A",
        channel: str = "ALL",
        target_audience: str = "ALL",
        tick: int = 0
    ) -> Dict[str, Any]:
        with self.lock:
            camp = {
                "id": campaign_id,
                "name": name,
                "tagline": tagline,
                "sector": sector,
                "price_inr": float(price_inr),
                "claimed_utility": float(claimed_utility),
                "actual_quality": float(actual_quality),
                "variant": variant,
                "channel": channel,
                "status": "ACTIVE",
                "created_tick": tick,
                "target_audience": target_audience,
                "impressions": self.campaigns.get(campaign_id, {}).get("impressions", 0),
                "clicks": self.campaigns.get(campaign_id, {}).get("clicks", 0),
                "purchases": self.campaigns.get(campaign_id, {}).get("purchases", 0),
                "revenue_inr": self.campaigns.get(campaign_id, {}).get("revenue_inr", 0.0),
                "promoters": self.campaigns.get(campaign_id, {}).get("promoters", 0),
                "passives": self.campaigns.get(campaign_id, {}).get("passives", 0),
                "detractors": self.campaigns.get(campaign_id, {}).get("detractors", 0),
            }
            self.campaigns[campaign_id] = camp

            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """INSERT OR REPLACE INTO consumer_campaigns 
                       (id, name, tagline, sector, price_inr, claimed_utility, actual_quality, 
                        variant, channel, status, created_tick, target_audience, impressions, 
                        clicks, purchases, revenue_inr, promoters, passives, detractors)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (camp["id"], camp["name"], camp["tagline"], camp["sector"], camp["price_inr"],
                     camp["claimed_utility"], camp["actual_quality"], camp["variant"], camp["channel"],
                     camp["status"], camp["created_tick"], camp["target_audience"], camp["impressions"],
                     camp["clicks"], camp["purchases"], camp["revenue_inr"], camp["promoters"],
                     camp["passives"], camp["detractors"])
                )
                conn.commit()

        return camp

    def create_ab_test(
        self,
        base_id: str,
        name: str,
        sector: str,
        variant_a_tagline: str,
        variant_a_price: float,
        variant_b_tagline: str,
        variant_b_price: float,
        claimed_utility: float = 8.5,
        actual_quality: float = 8.5,
        tick: int = 0
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        id_a = f"{base_id}-A"
        id_b = f"{base_id}-B"

        camp_a = self.create_or_update_campaign(
            campaign_id=id_a,
            name=f"{name} (Variant A)",
            tagline=variant_a_tagline,
            sector=sector,
            price_inr=variant_a_price,
            claimed_utility=claimed_utility,
            actual_quality=actual_quality,
            variant="A (Technical / Value)",
            channel="COMMUTE_BILLBOARD",
            tick=tick
        )

        camp_b = self.create_or_update_campaign(
            campaign_id=id_b,
            name=f"{name} (Variant B)",
            tagline=variant_b_tagline,
            sector=sector,
            price_inr=variant_b_price,
            claimed_utility=claimed_utility,
            actual_quality=actual_quality,
            variant="B (Hype / Scarcity)",
            channel="OASIS_SOCIAL_FEED",
            tick=tick
        )

        return camp_a, camp_b

    def get_sector_affinity(self, profile: Dict[str, Any], sector: str) -> float:
        mapping = {
            "TECH_DEV_TOOL": profile.get("tech_affinity", 1.0),
            "LIFESTYLE_LUXURY": profile.get("lifestyle_affinity", 1.0),
            "BEVERAGE_FOOD": profile.get("food_beverage_affinity", 1.0),
            "HEALTH_FITNESS": profile.get("fitness_affinity", 1.0),
            "FINTECH_SaaS": profile.get("fintech_affinity", 1.0),
            "ECO_MOBILITY": profile.get("mobility_affinity", 1.0)
        }
        return mapping.get(sector, 1.0)

    def evaluate_purchase_decision(
        self,
        citizen: Any,
        campaign: Dict[str, Any],
        tick: int,
        social_proof_score: float = 0.0
    ) -> Dict[str, Any]:
        cid = citizen.id if hasattr(citizen, "id") else citizen.get("citizen_id", "CIT_UNK")
        profile = self.register_or_update_profile(citizen)
        price = float(campaign["price_inr"])
        wallet = float(getattr(citizen, "wallet_inr", None) or citizen.get("wallet_inr", 25000.0))
        name = getattr(citizen, "name", None) or citizen.get("citizen_name", cid)
        role = getattr(citizen, "role", None) or citizen.get("role", "Citizen")

        if campaign["id"] in profile.get("inventory", []):
            return {
                "decision": "ALREADY_OWNED",
                "monologue": f"Already purchased {campaign['name']}. Running in daily workflow.",
                "price": price,
                "sentiment": 0.5
            }

        emergency_cushion = wallet * (1.0 - profile.get("discretionary_ratio", 0.25))
        discretionary_budget = max(0.0, wallet - emergency_cushion)

        if wallet < price:
            objection = "SOLVENCY_BUFFER_BREACH"
            monologue = (
                f"Cannot purchase {campaign['name']} (₹{price:,.0f}): "
                f"Total liquid wallet is ₹{wallet:,.0f}. Insolvent for this ticket size."
            )
            return {
                "decision": "REJECT_INSOLVENT",
                "objection_reason": objection,
                "monologue": monologue,
                "price": price,
                "sentiment": -0.4
            }

        if price > discretionary_budget and price > 1500.0:
            objection = "PRICE_RESISTANCE"
            monologue = (
                f"Passed on {campaign['name']} (₹{price:,.0f}): "
                f"Discretionary buffer is ₹{discretionary_budget:,.0f}. "
                f"Violates my financial prudence rules."
            )
            return {
                "decision": "REJECT_BUDGET",
                "objection_reason": objection,
                "monologue": monologue,
                "price": price,
                "sentiment": -0.2
            }

        affinity = self.get_sector_affinity(profile, campaign["sector"])
        skepticism = profile.get("brand_skepticism", 0.5)
        price_sens = profile.get("price_sensitivity", 0.5)
        claimed_utility = campaign.get("claimed_utility", 7.5)

        is_hype_ad = "B" in campaign.get("variant", "") or "Supercharge" in campaign.get("tagline", "")
        hype_penalty = 0.25 if (is_hype_ad and skepticism > 0.65) else 0.0

        effective_utility = claimed_utility * (1.0 - (skepticism * 0.5) - hype_penalty)
        perceived_value = effective_utility * affinity + (social_proof_score * 2.0)

        price_ratio = price / max(100.0, wallet)
        price_resistance = price_sens * (price_ratio * 15.0)

        decision_score = perceived_value - price_resistance + random.uniform(-0.5, 0.5)

        BUY_THRESHOLD = 6.8

        if decision_score >= BUY_THRESHOLD:
            if hasattr(citizen, "wallet_inr"):
                citizen.wallet_inr = max(0.0, wallet - price)
            profile.setdefault("inventory", []).append(campaign["id"])

            actual_quality = campaign.get("actual_quality", 7.5)
            satisfaction = actual_quality - (claimed_utility * 0.15)
            
            if satisfaction >= 7.5:
                nps_rating = random.randint(9, 10)
                sentiment = 0.85
                outcome_phrase = "Exceeds expectations. Absolutely worth the investment."
            elif satisfaction >= 6.0:
                nps_rating = random.randint(7, 8)
                sentiment = 0.35
                outcome_phrase = "Functional and covers basic requirements."
            else:
                nps_rating = random.randint(2, 6)
                sentiment = -0.50
                outcome_phrase = "Overpromised on utility. Performance did not match claims."

            monologue = (
                f"Purchased {campaign['name']} (₹{price:,.0f})! "
                f"Perceived value ({perceived_value:.1f}) beat price barrier. {outcome_phrase}"
            )

            result = {
                "decision": "PURCHASED",
                "objection_reason": None,
                "monologue": monologue,
                "price": price,
                "sentiment": sentiment,
                "nps_rating": nps_rating,
                "perceived_value": round(perceived_value, 2),
                "decision_score": round(decision_score, 2)
            }
        else:
            sentiment = -0.1
            nps_rating = random.randint(4, 6)
            if affinity < 0.8:
                objection = "LOW_CATEGORY_RELEVANCE"
                monologue = (
                    f"Passed on {campaign['name']} (₹{price:,.0f}): "
                    f"Category '{campaign['sector']}' has zero relevance to my role as {role}."
                )
            elif (skepticism * 0.5 + hype_penalty) > 0.45:
                objection = "BRAND_SKEPTICISM"
                monologue = (
                    f"Rejected {campaign['name']} (₹{price:,.0f}): "
                    f"Claims sound like marketing fluff. Need verified benchmarks before trusting."
                )
            elif price_resistance > perceived_value * 0.7:
                objection = "PRICE_RESISTANCE"
                monologue = (
                    f"Rejected {campaign['name']} (₹{price:,.0f}): "
                    f"Overpriced for the promised feature set. Value score ({perceived_value:.1f}) doesn't justify cost."
                )
            else:
                objection = "WEAK_AD_COPY"
                monologue = (
                    f"Ignored {campaign['name']} (₹{price:,.0f}): "
                    f"Ad copy did not communicate clear ROI or differentiated advantages."
                )

            result = {
                "decision": "REJECT_VALUE",
                "objection_reason": objection,
                "monologue": monologue,
                "price": price,
                "sentiment": sentiment,
                "nps_rating": nps_rating,
                "perceived_value": round(perceived_value, 2),
                "decision_score": round(decision_score, 2)
            }

        return result

    def step_marketing_diffusion(
        self,
        citizens: Dict[str, Any],
        tick: int,
        macro_economy: Optional[Any] = None
    ) -> Dict[str, Any]:
        if not self.campaigns:
            return {"status": "NO_CAMPAIGNS"}

        active_camps = [c for c in self.campaigns.values() if c.get("status") == "ACTIVE"]
        if not active_camps:
            return {"status": "NO_ACTIVE_CAMPAIGNS"}

        tick_events = []
        new_transactions = []
        macro_c_injection = 0.0

        sample_size = min(25, len(citizens))
        ad_targets = random.sample(list(citizens.values()), sample_size)

        for citizen in ad_targets:
            camp = random.choice(active_camps)
            camp_id = camp["id"]
            camp["impressions"] += 1

            profile = self.register_or_update_profile(citizen)
            social_proof = 0.0
            
            rels = getattr(citizen, "relationships", {})
            peer_ids = list(rels.keys()) if isinstance(rels, dict) else [r.get("with_id") for r in rels if isinstance(r, dict)]
            for peer_cid in peer_ids:
                peer_prof = self.consumer_profiles.get(peer_cid)
                if peer_prof and camp_id in peer_prof.get("inventory", []):
                    social_proof += 0.35 * peer_prof.get("influence_weight", 1.0)

            affinity = self.get_sector_affinity(profile, camp["sector"])
            ctr_prob = min(0.85, 0.25 * affinity + (social_proof * 0.2))
            
            c_name = getattr(citizen, "name", None) or citizen.get("citizen_name", "Citizen")
            c_id = getattr(citizen, "id", None) or citizen.get("citizen_id", "CIT")

            if random.random() <= ctr_prob:
                camp["clicks"] += 1
                decision_res = self.evaluate_purchase_decision(citizen, camp, tick, social_proof)

                if decision_res["decision"] == "PURCHASED":
                    camp["purchases"] += 1
                    camp["revenue_inr"] += decision_res["price"]
                    macro_c_injection += decision_res["price"]
                    
                    nps = decision_res.get("nps_rating", 8)
                    if nps >= 9:
                        camp["promoters"] += 1
                    elif nps >= 7:
                        camp["passives"] += 1
                    else:
                        camp["detractors"] += 1

                    tick_events.append({
                        "type": "PURCHASE",
                        "citizen": c_name,
                        "campaign": camp["name"],
                        "price": decision_res["price"],
                        "monologue": decision_res["monologue"]
                    })
                elif decision_res["decision"].startswith("REJECT"):
                    tick_events.append({
                        "type": "REJECTION",
                        "citizen": c_name,
                        "campaign": camp["name"],
                        "reason": decision_res.get("objection_reason"),
                        "monologue": decision_res["monologue"]
                    })

                new_transactions.append((
                    camp_id, c_id, c_name, tick, decision_res["price"],
                    decision_res["decision"], decision_res.get("objection_reason"),
                    decision_res["monologue"], decision_res.get("sentiment", 0.0),
                    decision_res.get("nps_rating", 7), 0, time.time()
                ))

        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                cur = conn.cursor()
                cur.executemany(
                    """INSERT INTO consumer_transactions 
                       (campaign_id, citizen_id, citizen_name, tick, price_inr, 
                        decision, objection_reason, thought_monologue, sentiment_score, 
                        nps_rating, wom_shared, timestamp)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    new_transactions
                )
                for camp in active_camps:
                    cur.execute(
                        """UPDATE consumer_campaigns 
                           SET impressions = ?, clicks = ?, purchases = ?, revenue_inr = ?, 
                               promoters = ?, passives = ?, detractors = ?
                           WHERE id = ?""",
                        (camp["impressions"], camp["clicks"], camp["purchases"], camp["revenue_inr"],
                         camp["promoters"], camp["passives"], camp["detractors"], camp["id"])
                    )
                conn.commit()

        diffusion_metrics = {}
        for camp in active_camps:
            total_m = 100.0
            n_t = float(camp["purchases"])
            promoters = float(camp["promoters"])
            detractors = float(camp["detractors"])
            
            p = 0.03
            q = max(0.0, 0.38 * (promoters / max(1.0, n_t)) - 0.20 * (detractors / max(1.0, n_t)))
            
            remaining_market = max(0.0, total_m - n_t)
            d_n = (p + q * (n_t / total_m)) * remaining_market
            
            k_factor = round((promoters * 1.5) / max(1.0, n_t), 2)
            total_responses = max(1.0, promoters + camp["passives"] + detractors)
            nps_score = round(((promoters - detractors) / total_responses) * 100, 1)

            if n_t >= 25 and k_factor >= 1.0:
                verdict = "VIRAL MARKET HIT (Exponential Adoption)"
            elif n_t >= 15:
                verdict = "SOLID NICHE PRODUCT-MARKET FIT"
            elif camp["clicks"] > 30 and n_t <= 3:
                verdict = "MARKET FAILURE: HIGH INTEREST, HIGH RESISTANCE"
            elif camp["clicks"] < 10 and camp["impressions"] > 40:
                verdict = "MARKET FAILURE: AD BLINDNESS / WEAK VALUE PROP"
            else:
                verdict = "EARLY ADOPTION TESTING (Gaining Traction)"

            diffusion_metrics[camp["id"]] = {
                "name": camp["name"],
                "variant": camp["variant"],
                "impressions": camp["impressions"],
                "clicks": camp["clicks"],
                "ctr_percent": round((camp["clicks"] / max(1, camp["impressions"])) * 100, 1),
                "purchases": camp["purchases"],
                "conversion_rate": round((camp["purchases"] / max(1, camp["clicks"])) * 100, 1),
                "revenue_inr": f"₹{camp['revenue_inr']:,.0f}",
                "promoters": camp["promoters"],
                "passives": camp["passives"],
                "detractors": camp["detractors"],
                "nps_score": nps_score,
                "k_factor": k_factor,
                "bass_p": round(p, 3),
                "bass_q": round(q, 3),
                "bass_projected_rate": round(d_n, 2),
                "verdict": verdict
            }

        return {
            "tick": tick,
            "new_purchases_count": len([e for e in tick_events if e["type"] == "PURCHASE"]),
            "macro_consumption_injected": macro_c_injection,
            "diffusion_metrics": diffusion_metrics,
            "events": tick_events
        }

    def run_synthetic_focus_group(
        self,
        question: str,
        campaign_id: Optional[str] = None,
        cohort_filter: str = "ALL",
        citizens: Optional[Dict[str, Any]] = None,
        tick: int = 0
    ) -> Dict[str, Any]:
        if not citizens:
            c_list = list(self.consumer_profiles.values())
        else:
            c_list = [self.register_or_update_profile(c) for c in citizens.values()]

        cohort = []
        for p in c_list:
            role = p.get("role", "")
            dept = p.get("department", "")
            if cohort_filter == "ALL":
                cohort.append(p)
            elif cohort_filter == "TECH_FOUNDERS_ARCHITECTS":
                if any(w in dept.lower() or w in role.lower() for w in ["architecture", "kernel", "founder", "devops", "systems", "engineer"]):
                    cohort.append(p)
            elif cohort_filter == "HOSPITALITY_ARTISANS":
                if any(w in dept.lower() or w in role.lower() for w in ["hospitality", "culinary", "barista", "chef", "media", "culture"]):
                    cohort.append(p)
            elif cohort_filter == "PARENTS_FAMILIES":
                if any(w in role.lower() for w in ["lead", "architect", "director", "manager", "captain"]):
                    cohort.append(p)

        if not cohort:
            cohort = c_list[:20]

        camp = self.campaigns.get(campaign_id) if campaign_id else None
        target_name = camp["name"] if camp else "New Bengaluru Innovation"

        # Dynamically extract ticket price from query or campaign
        target_price = camp["price_inr"] if camp else 2500.0
        price_match = re.search(r'(?:₹|rs\.?|inr|\$)?\s*([0-9]+(?:,[0-9]{3})*(?:\.[0-9]+)?)', question, re.IGNORECASE)
        if price_match:
            try:
                parsed_p = float(price_match.group(1).replace(',', ''))
                if parsed_p > 0:
                    target_price = parsed_p
            except Exception:
                pass

        # Detect product sector & category
        q_lower = (question + " " + target_name).lower()
        if any(w in q_lower for w in ["ai", "ebpf", "kernel", "profiler", "saas", "code", "dev", "ide", "api", "cloud", "model"]):
            detected_sector = "TECH_DEV_TOOL"
        elif any(w in q_lower for w in ["coffee", "roast", "beer", "pub", "brew", "dosa", "food", "cafe", "snack", "restaurant"]):
            detected_sector = "HOSPITALITY_ARTISAN"
        elif any(w in q_lower for w in ["gym", "cult", "fitness", "yoga", "health", "workout", "protein"]):
            detected_sector = "FITNESS_WELLNESS"
        elif any(w in q_lower for w in ["metro", "cab", "ola", "uber", "bike", "scooter", "transit", "bus"]):
            detected_sector = "URBAN_MOBILITY"
        elif any(w in q_lower for w in ["crypto", "token", "web3", "nft", "trading", "invest", "fintech"]):
            detected_sector = "FINTECH_DEFI"
        else:
            detected_sector = "GENERAL_CONSUMER"

        # Check for hype / buzzword red flags that trigger Bangalore citizen skepticism
        hype_triggers = [w for w in ["revolution", "supercharge", "10x", "guaranteed", "hyper-scale", "crypto", "magic", "disrupt", "next-gen", "ultra"] if w in q_lower]
        has_hype_red_flag = len(hype_triggers) > 0

        sentiment_buckets = {"ENTHUSIASTIC_BUYER": 0, "SKEPTICAL_CONSIDERATION": 0, "PRICE_RESISTANT": 0, "STRONG_PASS": 0}
        quotes = []
        failure_objection_counts = {"SOLVENCY": 0, "BUDGET_CAP": 0, "SKEPTICISM_HYPE": 0, "IRRELEVANT_CATEGORY": 0, "FREE_ALT_EXISTS": 0}

        for member in cohort:
            name = member.get("citizen_name", "Citizen")
            role = member.get("role", "Citizen")
            dept = member.get("department", "General")
            wallet = member.get("wallet_inr", 25000.0)
            disc_ratio = member.get("discretionary_ratio", 0.25)
            disc_budget = wallet * disc_ratio
            skepticism = member.get("brand_skepticism", 0.5)
            price_sens = member.get("price_sensitivity", 0.5)
            affinity = self.get_sector_affinity(member, detected_sector)

            # Strict Unvarnished Evaluation Logic
            # 1. Ticket size insolvency
            if target_price > wallet:
                bucket = "STRONG_PASS"
                failure_objection_counts["SOLVENCY"] += 1
                quote = f"Insolvent for this price. My entire liquid wallet is ₹{wallet:,.0f} and the asking price is ₹{target_price:,.0f}. Pure financial fantasy."
            # 2. Discretionary budget breach
            elif target_price > disc_budget and target_price > 1200.0:
                bucket = "PRICE_RESISTANT"
                failure_objection_counts["BUDGET_CAP"] += 1
                quote = f"Discretionary monthly ceiling is ₹{disc_budget:,.0f}. Charging ₹{target_price:,.0f} is an immediate pass. We have rent and groceries in Bangalore."
            # 3. Category relevance mismatch
            elif affinity < 0.85:
                bucket = "STRONG_PASS"
                failure_objection_counts["IRRELEVANT_CATEGORY"] += 1
                quote = f"In {dept} as {role}, this offers zero daily utility. Solving a problem I do not have."
            # 4. Hype red flags & high skepticism
            elif has_hype_red_flag and skepticism >= 0.58:
                bucket = "SKEPTICAL_CONSIDERATION"
                failure_objection_counts["SKEPTICISM_HYPE"] += 1
                quote = f"Claims of '{', '.join(hype_triggers)}' are red flags. In Bangalore we've seen dozens of wrapper startups fail. Show reproducible benchmarks, not PR."
            # 5. High skepticism even without overt hype
            elif skepticism >= 0.72:
                bucket = "SKEPTICAL_CONSIDERATION"
                failure_objection_counts["FREE_ALT_EXISTS"] += 1
                quote = "Unconvinced. Existing open-source tools or traditional workflows work fine. Why pay a vendor tax?"
            # 6. Price sensitivity resistance
            elif price_sens > 0.65 and target_price > 800.0:
                bucket = "PRICE_RESISTANT"
                failure_objection_counts["BUDGET_CAP"] += 1
                quote = "Price is inflated for the promised utility. Would consider at 60% discount or a freemium tier."
            # 7. Genuinely passes all filters
            else:
                bucket = "ENTHUSIASTIC_BUYER"
                quote = f"Hits my exact pain point in {dept}. At ₹{target_price:,.0f}, the unit economics justify immediate adoption."

            sentiment_buckets[bucket] += 1
            quotes.append({
                "citizen_name": name,
                "role": role,
                "department": dept,
                "bucket": bucket,
                "quote": quote
            })

        total = max(1, len(cohort))
        enthusiastic_pct = round((sentiment_buckets["ENTHUSIASTIC_BUYER"] / total) * 100, 1)
        skeptical_pct = round((sentiment_buckets["SKEPTICAL_CONSIDERATION"] / total) * 100, 1)
        price_resistant_pct = round((sentiment_buckets["PRICE_RESISTANT"] / total) * 100, 1)
        strong_pass_pct = round((sentiment_buckets["STRONG_PASS"] / total) * 100, 1)

        # UNVARNISHED REAL-WORLD TRUTH ENGINE
        is_failure = enthusiastic_pct < 38.0
        
        if is_failure:
            if price_resistant_pct >= 40.0 or failure_objection_counts["BUDGET_CAP"] + failure_objection_counts["SOLVENCY"] >= total * 0.4:
                verdict = "🚨 COMMERCIAL FAILURE: SEVERE UNIT ECONOMICS & PRICING SUICIDE"
                primary_failure_driver = "PRICING_DISCREPANCY"
            elif skeptical_pct >= 35.0 or failure_objection_counts["SKEPTICISM_HYPE"] >= total * 0.3:
                verdict = "🚨 COMMERCIAL FAILURE: HYPER-SKEPTICISM & CREDIBILITY COLLAPSE"
                primary_failure_driver = "CREDIBILITY_DEFICIT"
            elif strong_pass_pct >= 45.0:
                verdict = "🚨 COMMERCIAL FAILURE: ZERO PRODUCT-MARKET FIT (DEAD ON ARRIVAL)"
                primary_failure_driver = "IRRELEVANT_UTILITY"
            else:
                verdict = "🚨 COMMERCIAL FAILURE: HIGH-CHURN ACQUISITION TRAP"
                primary_failure_driver = "POOR_RETENTION_DYNAMICS"

            mistakes_made = [
                f"1. Pricing Delusion: ₹{target_price:,.0f} exceeds the median discretionary threshold of Bangalore workers by {(target_price/max(500, total)):.1f}x.",
                f"2. Credibility Deficit: {('Hype buzzwords (' + ', '.join(hype_triggers) + ') triggered defensive skepticism') if has_hype_red_flag else 'No tangible technical proof or peer endorsements provided.'}",
                "3. Phantom Job-To-Be-Done: Failed to demonstrate why users should discard established alternatives (free OSS or local staples).",
                f"4. Solvency Friction: Breached the liquid savings buffer for {failure_objection_counts['SOLVENCY']} cohort members.",
                "5. CAC/LTV Catastrophe: Projected customer acquisition cost exceeds lifetime value by 300%+, leading to burn rate insolvency in 45-60 days."
            ]

            financial_autopsy = {
                "commercial_status": "FAILED_UNVIABLE",
                "projected_cac_inr": round(target_price * 4.2, 0),
                "projected_ltv_inr": round(target_price * 1.1, 0),
                "payback_period_months": 22.5,
                "burn_kill_horizon_days": 48,
                "nps_rating": round(max(-100, (enthusiastic_pct - (skeptical_pct + price_resistant_pct + strong_pass_pct))), 1),
                "viral_k_factor": 0.08
            }

            honest_prescription = (
                f"DO NOT LAUNCH in current state. Slash ticket price to ₹{max(299, round(target_price * 0.35, -1)):,.0f}, "
                f"strip all buzzwords, provide transparent reproducible benchmarks, and focus strictly on {detected_sector} power users."
            )
        else:
            verdict = "✓ VIABLE PRODUCT-MARKET FIT VALIDATED (Niche Adoption Confirmed)"
            primary_failure_driver = "NONE_ACTIVE"
            mistakes_made = [
                "1. Caution: High initial skepticism remains in 25%+ of senior architects; ensure day-1 onboarding friction is near zero.",
                "2. Churn Risk: Ensure post-purchase actual quality matches claimed utility to avoid negative viral word-of-mouth.",
                "3. Expansion Ceiling: Address price resistance before attempting mass-market urban rollout."
            ]
            financial_autopsy = {
                "commercial_status": "VIABLE_NICHE",
                "projected_cac_inr": round(target_price * 1.2, 0),
                "projected_ltv_inr": round(target_price * 3.8, 0),
                "payback_period_months": 3.4,
                "burn_kill_horizon_days": 365,
                "nps_rating": round(enthusiastic_pct - (skeptical_pct * 0.5), 1),
                "viral_k_factor": 1.24
            }
            honest_prescription = "Clear to run targeted pilot in specific hubs (Indiranagar / Koramangala / HSR). Maintain transparent technical documentation."

        summary = {
            "total_cohort_size": total,
            "cohort_filter": cohort_filter,
            "target_product": target_name,
            "target_price_inr": target_price,
            "detected_sector": detected_sector,
            "question": question,
            "enthusiastic_percent": enthusiastic_pct,
            "skeptical_percent": skeptical_pct,
            "price_resistant_percent": price_resistant_pct,
            "strong_pass_percent": strong_pass_pct,
            "is_commercial_failure": is_failure,
            "consensus_verdict": verdict,
            "primary_failure_driver": primary_failure_driver,
            "mistakes_made": mistakes_made,
            "financial_autopsy": financial_autopsy,
            "honest_prescription": honest_prescription
        }

        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """INSERT INTO consumer_focus_groups 
                       (campaign_id, question, cohort_filter, tick, summary_json, quotes_json, timestamp)
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (campaign_id or "GENERAL", question, cohort_filter, tick,
                     json.dumps(summary), json.dumps(quotes[:15]), time.time())
                )
                conn.commit()

        return {
            "summary": summary,
            "quotes": quotes[:12],
            "forensic_autopsy": financial_autopsy,
            "mistakes_made": mistakes_made,
            "honest_prescription": honest_prescription
        }

    def get_campaign_analytics(self) -> Dict[str, Any]:
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                camps = [dict(r) for r in conn.execute("SELECT * FROM consumer_campaigns").fetchall()]
                tx_rows = conn.execute(
                    """SELECT campaign_id, citizen_name, decision, objection_reason, 
                              thought_monologue, price_inr, nps_rating, tick 
                       FROM consumer_transactions 
                       ORDER BY id DESC LIMIT 40"""
                ).fetchall()
                recent_txs = [dict(r) for r in tx_rows]
                
                objection_counts = {}
                for r in conn.execute(
                    """SELECT objection_reason, COUNT(*) as cnt 
                       FROM consumer_transactions 
                       WHERE objection_reason IS NOT NULL 
                       GROUP BY objection_reason"""
                ).fetchall():
                    objection_counts[r["objection_reason"]] = r["cnt"]

                fg_rows = conn.execute(
                    """SELECT id, campaign_id, question, cohort_filter, tick, summary_json, quotes_json, timestamp 
                       FROM consumer_focus_groups 
                       ORDER BY id DESC LIMIT 5"""
                ).fetchall()
                recent_fgs = []
                for r in fg_rows:
                    recent_fgs.append({
                        "id": r["id"],
                        "campaign_id": r["campaign_id"],
                        "question": r["question"],
                        "cohort_filter": r["cohort_filter"],
                        "tick": r["tick"],
                        "summary": json.loads(r["summary_json"]),
                        "quotes": json.loads(r["quotes_json"])
                    })

        campaign_cards = []
        for c in camps:
            impr = max(1, c["impressions"])
            clicks = c["clicks"]
            purchases = c["purchases"]
            ctr = round((clicks / impr) * 100, 1)
            cvr = round((purchases / max(1, clicks)) * 100, 1)
            prom = c["promoters"]
            detr = c["detractors"]
            tot_resp = max(1, prom + c["passives"] + detr)
            nps = round(((prom - detr) / tot_resp) * 100, 1)
            k_factor = round((prom * 1.5) / max(1.0, purchases), 2)

            campaign_cards.append({
                "id": c["id"],
                "name": c["name"],
                "tagline": c["tagline"],
                "sector": c["sector"],
                "price_inr": c["price_inr"],
                "variant": c["variant"],
                "channel": c["channel"],
                "status": c["status"],
                "impressions": c["impressions"],
                "clicks": clicks,
                "purchases": purchases,
                "revenue_inr": f"₹{c['revenue_inr']:,.0f}",
                "ctr_percent": ctr,
                "cvr_percent": cvr,
                "promoters": prom,
                "passives": c["passives"],
                "detractors": detr,
                "nps_score": nps,
                "k_factor": k_factor,
                "verdict": (
                    "VIRAL HIT (K > 1.0)" if k_factor >= 1.0 and purchases >= 10
                    else "MARKET ATTRACTION" if purchases >= 5
                    else "MARKET RESISTANCE" if clicks > 15 and purchases <= 2
                    else "TESTING FLIGHT"
                )
            })

        return {
            "campaigns": campaign_cards,
            "recent_monologues": recent_txs,
            "objection_breakdown": objection_counts,
            "recent_focus_groups": recent_fgs,
            "total_campaigns": len(campaign_cards),
            "total_market_revenue": f"₹{sum(c['revenue_inr'] for c in camps):,.0f}"
        }
