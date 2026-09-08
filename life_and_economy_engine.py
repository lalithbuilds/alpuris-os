"""
Bengaluru Living Metropolis OS — Life, Family, Entrepreneurship & Macro-GDP Engine
Drives:
1. Work, Careers, Salaries, Promotions & Real-World Living Expenses
2. Dating, Romance, Weddings, Marriage & Family Households
3. Children, Lineage Generations & Education
4. Travel, Leisure Outings & Vacations (Nandi Hills, UB City, Cubbon Park, Airport)
5. Founding Startups, Angel Investing, Equity, Wealth Compounding & Money Doubling (2x, 4x, 8x)
6. Real Macro-GDP Engine based on Standard National Accounting: GDP = C + I + G + NX
"""

import time
import math
import random
import sqlite3
import threading
from typing import Dict, List, Any, Optional, Tuple

DB_PATH = "/Users/lalith/ray_agent_world/world_memory.sqlite"

# Startup archetypes founded by ambitious Bangalore citizens
STARTUP_TEMPLATES = [
    {"name": "NammaMind AI Labs", "sector": "Autonomous AI Agents", "base_val": 4500000.0, "rev_factor": 0.18},
    {"name": "BharatPay Protocol", "sector": "Decentralized Fintech", "base_val": 6000000.0, "rev_factor": 0.22},
    {"name": "Koramangala Hops & Brews", "sector": "Craft Microbrewery", "base_val": 2500000.0, "rev_factor": 0.30},
    {"name": "GreenSilk EV Mobility", "sector": "Smart Urban Transit", "base_val": 3800000.0, "rev_factor": 0.20},
    {"name": "Atraxia Bio-Genomics", "sector": "Precision Therapeutics", "base_val": 8000000.0, "rev_factor": 0.15},
    {"name": "Whitefield Cloud Mesh", "sector": "Edge Distributed Storage", "base_val": 5200000.0, "rev_factor": 0.24},
    {"name": "Vidyarthi Fast Foods", "sector": "Artisan Darshini Chain", "base_val": 1800000.0, "rev_factor": 0.35},
    {"name": "Indiranagar Robotics Co", "sector": "Actuator Hardware", "base_val": 7000000.0, "rev_factor": 0.17}
]

# Leisure & Vacation Destinations
TRAVEL_DESTINATIONS = [
    {"name": "Nandi_Hills_Sunrise", "desc": "Early morning drive up Nandi Hills peak to watch the cloud sunrise", "cost": 1800.0, "joy": 22},
    {"name": "UB_City_Luxury_Dining", "desc": "Skyline rooftop dining & cocktails on the 16th floor at UB City", "cost": 3500.0, "joy": 25},
    {"name": "Nexus_Koramangala_Mall", "desc": "Weekend retail shopping spree, arcade gaming and IMAX movies", "cost": 2200.0, "joy": 18},
    {"name": "Cubbon_Park_Family_Picnic", "desc": "Picnic under flowering Gulmohar trees and feeding ducks by the fountain", "cost": 450.0, "joy": 20},
    {"name": "Kempegowda_Airport_Vacation", "desc": "Weekend flight getaway to Goa & Andaman beaches", "cost": 8500.0, "joy": 32},
    {"name": "Koramangala_Microbrewery_Pub", "desc": "Late-night craft stout tasting & indie rock acoustic session", "cost": 1400.0, "joy": 20}
]

# Baby names for Bangalore families
CHILD_NAMES = [
    "Aarohi", "Vihaan", "Ananya", "Ishaan", "Diya", "Reyansh", "Saanvi", "Kabir",
    "Advait", "Meera", "Arjun", "Tara", "Rishi", "Aditi", "Dev", "Anika",
    "Dhruv", "Riya", "Yuvan", "Pooja", "Samarth", "Nandini", "Kavya", "Tejas"
]

SCHOOLS = [
    "National Public School (Indiranagar)",
    "Delhi Public School (Bangalore East)",
    "The International School Bangalore (TISB)",
    "Kendriya Vidyalaya (IISc Campus)",
    "Bishop Cotton Boys/Girls School",
    "Mallya Aditi International School"
]

class LifeAndEconomyEngine:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self.lock = threading.Lock()
        
        # In-memory fast state caches
        self.citizen_records: Dict[str, Dict[str, Any]] = {}
        self.companies: List[Dict[str, Any]] = []
        self.milestones: List[Dict[str, Any]] = []
        
        # Real-time transaction flow accumulator per tick (INR)
        self.flow_ledger = {
            "consumption_inr": 0.0,
            "investment_inr": 0.0,
            "govt_spending_inr": 0.0,
            "tax_collected_inr": 0.0,
            "exports_inr": 0.0
        }
        
        # Macro-GDP Accounting state (in Crores INR)
        # GDP = C + I + G + NX
        self.macro_gdp = {
            "gdp_crores": 3850.50,
            "previous_gdp": 3820.00,
            "annual_growth_rate": 8.6,
            "consumption_c_cr": 2150.20,
            "investment_i_cr": 980.40,
            "govt_spending_g_cr": 420.10,
            "net_exports_nx_cr": 299.80,
            "city_treasury_inr": 85000000.0,
            "inflation_rate": 4.2
        }
        
        self._init_db()
        self._load_state()

    def _init_db(self):
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            
            # Citizen Life, Romance, Career & Wealth Record
            cur.execute("""
                CREATE TABLE IF NOT EXISTS citizen_life_records (
                    citizen_id TEXT PRIMARY KEY,
                    citizen_name TEXT NOT NULL,
                    career_level INTEGER DEFAULT 2,       -- 1=Junior, 2=Mid, 3=Senior/Lead, 4=Director/Architect, 5=Founder/CXO
                    salary_inr REAL DEFAULT 4500.0,
                    marital_status TEXT DEFAULT 'SINGLE',  -- SINGLE, DATING, ENGAGED, MARRIED
                    partner_id TEXT,
                    partner_name TEXT,
                    romance_score REAL DEFAULT 0.0,
                    wedding_tick INTEGER,
                    children_json TEXT DEFAULT '[]',
                    happiness REAL DEFAULT 75.0,           -- 0 to 100
                    initial_net_worth REAL DEFAULT 25000.0,
                    current_net_worth REAL DEFAULT 25000.0,
                    doubling_count INTEGER DEFAULT 0,
                    company_id INTEGER,
                    vacation_count INTEGER DEFAULT 0,
                    last_vacation_tick INTEGER DEFAULT 0
                )
            """)
            
            # Companies / Startups Registry
            cur.execute("""
                CREATE TABLE IF NOT EXISTS companies_registry (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    sector TEXT NOT NULL,
                    founder_id TEXT NOT NULL,
                    founder_name TEXT NOT NULL,
                    valuation_inr REAL NOT NULL,
                    quarterly_rev_inr REAL NOT NULL,
                    employees_json TEXT DEFAULT '[]',
                    created_tick INTEGER NOT NULL
                )
            """)
            
            # Macro Economy History Ledger
            cur.execute("""
                CREATE TABLE IF NOT EXISTS macro_economy_ledger (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tick INTEGER NOT NULL,
                    gdp_crores REAL NOT NULL,
                    gdp_growth REAL NOT NULL,
                    consumption_cr REAL NOT NULL,
                    investment_cr REAL NOT NULL,
                    govt_cr REAL NOT NULL,
                    net_exports_cr REAL NOT NULL,
                    timestamp REAL NOT NULL
                )
            """)
            
            # Life Milestone Event Feed
            cur.execute("""
                CREATE TABLE IF NOT EXISTS life_milestones (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tick INTEGER NOT NULL,
                    event_type TEXT NOT NULL,             -- WEDDING, BIRTH, STARTUP_LAUNCH, WEALTH_DOUBLED, VACATION, PROMOTION
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    citizens_involved TEXT,
                    highlight_icon TEXT DEFAULT '✨',
                    created_at REAL NOT NULL
                )
            """)
            
            conn.commit()
            conn.close()

    def _load_state(self):
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            
            # Load citizen records
            cur.execute("SELECT * FROM citizen_life_records")
            rows = cur.fetchall()
            for r in rows:
                self.citizen_records[r[0]] = {
                    "citizen_id": r[0], "citizen_name": r[1], "career_level": r[2],
                    "salary_inr": r[3], "marital_status": r[4], "partner_id": r[5],
                    "partner_name": r[6], "romance_score": r[7], "wedding_tick": r[8],
                    "children": eval(r[9]) if r[9] else [], "happiness": r[10],
                    "initial_net_worth": r[11], "current_net_worth": r[12],
                    "doubling_count": r[13], "company_id": r[14],
                    "vacation_count": r[15], "last_vacation_tick": r[16]
                }
                
            # Load companies
            cur.execute("SELECT * FROM companies_registry ORDER BY valuation_inr DESC")
            c_rows = cur.fetchall()
            self.companies = [
                {
                    "id": c[0], "name": c[1], "sector": c[2], "founder_id": c[3],
                    "founder_name": c[4], "valuation_inr": c[5], "revenue_inr": c[6],
                    "employees": eval(c[7]) if c[7] else [], "created_tick": c[8]
                }
                for c in c_rows
            ]
            
            # Load milestones
            cur.execute("SELECT event_type, title, description, highlight_icon, tick FROM life_milestones ORDER BY id DESC LIMIT 15")
            m_rows = cur.fetchall()
            self.milestones = [
                {"type": m[0], "title": m[1], "desc": m[2], "icon": m[3], "tick": m[4]}
                for m in m_rows
            ]
            
            conn.close()

    def register_or_get_citizen(self, p) -> Dict[str, Any]:
        """Ensures a citizen has a full life record initialized."""
        if p.id in self.citizen_records:
            return self.citizen_records[p.id]
            
        role_l = p.role.lower()
        if "chief" in role_l or "principal" in role_l or "vp" in role_l or "head" in role_l:
            c_lvl = 4
            base_sal = 18000.0
        elif "lead" in role_l or "senior" in role_l or "manager" in role_l:
            c_lvl = 3
            base_sal = 9500.0
        elif "junior" in role_l or "intern" in role_l or "associate" in role_l:
            c_lvl = 1
            base_sal = 2800.0
        else:
            c_lvl = 2
            base_sal = 5500.0

        initial_nw = p.wallet_inr
        rec = {
            "citizen_id": p.id,
            "citizen_name": p.name,
            "career_level": c_lvl,
            "salary_inr": base_sal,
            "marital_status": "SINGLE",
            "partner_id": None,
            "partner_name": None,
            "romance_score": 0.0,
            "wedding_tick": None,
            "children": [],
            "happiness": round(random.uniform(70.0, 85.0), 1),
            "initial_net_worth": initial_nw,
            "current_net_worth": initial_nw,
            "doubling_count": 0,
            "company_id": None,
            "vacation_count": 0,
            "last_vacation_tick": 0
        }
        self.citizen_records[p.id] = rec
        self._persist_citizen(rec)
        return rec

    def _persist_citizen(self, rec: Dict[str, Any]):
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO citizen_life_records (
                    citizen_id, citizen_name, career_level, salary_inr, marital_status,
                    partner_id, partner_name, romance_score, wedding_tick, children_json,
                    happiness, initial_net_worth, current_net_worth, doubling_count,
                    company_id, vacation_count, last_vacation_tick
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(citizen_id) DO UPDATE SET
                    career_level=excluded.career_level,
                    salary_inr=excluded.salary_inr,
                    marital_status=excluded.marital_status,
                    partner_id=excluded.partner_id,
                    partner_name=excluded.partner_name,
                    romance_score=excluded.romance_score,
                    wedding_tick=excluded.wedding_tick,
                    children_json=excluded.children_json,
                    happiness=excluded.happiness,
                    current_net_worth=excluded.current_net_worth,
                    doubling_count=excluded.doubling_count,
                    company_id=excluded.company_id,
                    vacation_count=excluded.vacation_count,
                    last_vacation_tick=excluded.last_vacation_tick
            """, (
                rec["citizen_id"], rec["citizen_name"], rec["career_level"], rec["salary_inr"],
                rec["marital_status"], rec["partner_id"], rec["partner_name"], rec["romance_score"],
                rec["wedding_tick"], str(rec["children"]), rec["happiness"], rec["initial_net_worth"],
                rec["current_net_worth"], rec["doubling_count"], rec["company_id"],
                rec["vacation_count"], rec["last_vacation_tick"]
            ))
            conn.commit()
            conn.close()

    def record_milestone(self, m_type: str, title: str, desc: str, icon: str, tick: int, citizens: str = ""):
        m = {"type": m_type, "title": title, "desc": desc, "icon": icon, "tick": tick, "citizens": citizens}
        self.milestones.insert(0, m)
        if len(self.milestones) > 20:
            self.milestones.pop()
            
        with self.lock:
            conn = sqlite3.connect(self.db_path)
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO life_milestones (tick, event_type, title, description, citizens_involved, highlight_icon, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (tick, m_type, title, desc, citizens, icon, time.time()))
            conn.commit()
            conn.close()

    def step_citizen_life(self, p, tick: int, circadian_phase: str, all_personas: Dict[str, Any]) -> Dict[str, Any]:
        """Executes full work, salary, living costs, romance, family, travel & wealth compounding."""
        rec = self.register_or_get_citizen(p)
        events_generated = []
        loc = p.location

        # 1. WORK & SALARY (Earning with tax withholding TDS funding municipal treasury)
        is_work_hours = ("Morning" in circadian_phase or "Active" in circadian_phase)
        if is_work_hours:
            salary = rec["salary_inr"]
            tax_withheld = round(salary * 0.10, 2)
            net_salary = round(salary - tax_withheld, 2)
            p.earn_inr(net_salary, f"Net Salary for {p.role}")
            with self.lock:
                self.macro_gdp["city_treasury_inr"] += tax_withheld
                self.flow_ledger["tax_collected_inr"] += tax_withheld
            rec["happiness"] = min(100.0, rec["happiness"] + 0.8)
            
            # Promotion check
            if random.random() < 0.04 and rec["career_level"] < 5:
                rec["career_level"] += 1
                rec["salary_inr"] = round(rec["salary_inr"] * 1.35, 0)
                rec["happiness"] = min(100.0, rec["happiness"] + 15.0)
                title = f"PROMOTION: {p.name} promoted to Level {rec['career_level']}!"
                desc = f"{p.name} earned a leadership promotion. New salary: ₹{int(rec['salary_inr'])}/tick."
                self.record_milestone("PROMOTION", title, desc, "🎖️", tick, p.name)
                events_generated.append(title)

        # 2. LIVING EXPENSES & ENJOYMENT (Spending in Bengaluru with strict flow tracking)
        # Rent & Housing
        rent_cost = 450.0 if "HSR" in p.home_zone else 650.0
        if p.spend_inr(rent_cost, f"Apartment rent in {p.home_zone.replace('_', ' ')}"):
            with self.lock:
                self.flow_ledger["consumption_inr"] += rent_cost
        else:
            rec["happiness"] = max(10.0, rec["happiness"] - 2.0)

        # Location-based dynamic consumption
        if "Cafe" in loc or "Church" in loc:
            cost = round(random.uniform(120.0, 350.0), 2)
            if p.spend_inr(cost, "Artisan filter coffee and breakfast"):
                rec["happiness"] = min(100.0, rec["happiness"] + 1.5)
                with self.lock: self.flow_ledger["consumption_inr"] += cost
        elif "Pub" in loc or "Brewery" in loc:
            cost = round(random.uniform(650.0, 1600.0), 2)
            if p.spend_inr(cost, "Craft microbrewery beer flight & gourmet nachos"):
                rec["happiness"] = min(100.0, rec["happiness"] + 3.0)
                p.adjust_energy(4.0)
                with self.lock: self.flow_ledger["consumption_inr"] += cost
        elif "Gym" in loc or "Fit" in loc:
            cost = 350.0
            if p.spend_inr(cost, "Cult.fit strength & conditioning pass"):
                p.adjust_energy(10.0)
                rec["happiness"] = min(100.0, rec["happiness"] + 2.5)
                with self.lock: self.flow_ledger["consumption_inr"] += cost
        elif "Mall" in loc:
            cost = round(random.uniform(800.0, 3200.0), 2)
            if p.spend_inr(cost, "Electronics & lifestyle shopping at Nexus Mall"):
                rec["happiness"] = min(100.0, rec["happiness"] + 4.0)
                with self.lock: self.flow_ledger["consumption_inr"] += cost

        # Childcare & education expenses if parents
        if rec["children"]:
            child_expense = len(rec["children"]) * 850.0
            if p.spend_inr(child_expense, "Children education, tuition & supplies"):
                with self.lock: self.flow_ledger["consumption_inr"] += child_expense

        # 3. ROMANCE, DATING, MARRIAGE & WEDDINGS
        if rec["marital_status"] == "SINGLE":
            # Search for potential dating partner in same zone or social circle
            if random.random() < 0.18:
                candidates = [
                    op for op in all_personas.values()
                    if op.id != p.id and self.register_or_get_citizen(op)["marital_status"] == "SINGLE"
                ]
                # Prioritize same location
                same_loc = [c for c in candidates if c.location == p.location]
                chosen = random.choice(same_loc) if same_loc else (random.choice(candidates) if candidates else None)
                if chosen:
                    op_rec = self.register_or_get_citizen(chosen)
                    rec["partner_id"] = chosen.id
                    rec["partner_name"] = chosen.name
                    rec["romance_score"] = 55.0
                    rec["marital_status"] = "DATING"
                    
                    op_rec["partner_id"] = p.id
                    op_rec["partner_name"] = p.name
                    op_rec["romance_score"] = 55.0
                    op_rec["marital_status"] = "DATING"
                    self._persist_citizen(op_rec)
                    
                    title = f"ROMANCE: {p.name} and {chosen.name} started dating!"
                    desc = f" sparks ignited over coffee and conversations at {p.location.replace('_', ' ')}."
                    self.record_milestone("DATING", title, desc, "❤️", tick, f"{p.name} & {chosen.name}")
                    events_generated.append(title)

        elif rec["marital_status"] == "DATING":
            partner = all_personas.get(rec["partner_id"])
            if partner:
                op_rec = self.register_or_get_citizen(partner)
                # Grow romance
                rec["romance_score"] = min(100.0, rec["romance_score"] + random.uniform(4.0, 9.0))
                op_rec["romance_score"] = rec["romance_score"]
                
                # Propose & Engagement
                if rec["romance_score"] >= 80.0 and random.random() < 0.30:
                    rec["marital_status"] = "ENGAGED"
                    op_rec["marital_status"] = "ENGAGED"
                    p.spend_inr(4500.0, "Diamond solitaire engagement ring")
                    rec["happiness"] = min(100.0, rec["happiness"] + 20.0)
                    op_rec["happiness"] = min(100.0, op_rec["happiness"] + 20.0)
                    self._persist_citizen(op_rec)
                    
                    title = f"ENGAGEMENT: {p.name} & {partner.name} are engaged!"
                    desc = f"Romantic proposal at {p.location.replace('_', ' ')} accepted with a ring!"
                    self.record_milestone("ENGAGEMENT", title, desc, "💍", tick, f"{p.name} & {partner.name}")
                    events_generated.append(title)

        elif rec["marital_status"] == "ENGAGED":
            partner = all_personas.get(rec["partner_id"])
            if partner:
                op_rec = self.register_or_get_citizen(partner)
                # Marriage ceremony
                if (p.wallet_inr + partner.wallet_inr > 40000.0 or random.random() < 0.25):
                    rec["marital_status"] = "MARRIED"
                    rec["wedding_tick"] = tick
                    op_rec["marital_status"] = "MARRIED"
                    op_rec["wedding_tick"] = tick
                    
                    # Wedding reception expenses & celebration
                    wedding_cost = 12000.0
                    p.spend_inr(wedding_cost / 2, "Bengaluru Wedding Feast & Celebration")
                    partner.spend_inr(wedding_cost / 2, "Bengaluru Wedding Feast & Celebration")
                    
                    rec["happiness"] = 100.0
                    op_rec["happiness"] = 100.0
                    self._persist_citizen(op_rec)
                    
                    title = f"WEDDING: {p.name} & {partner.name} tied the knot!"
                    desc = "Grand traditional & tech Bengaluru wedding at Vidhana Soudha Registrar. Joint household established!"
                    self.record_milestone("WEDDING", title, desc, "👰🤵", tick, f"{p.name} & {partner.name}")
                    events_generated.append(title)

        # 4. CHILDREN & FAMILY GENERATIONS (Having Kids)
        if rec["marital_status"] == "MARRIED" and len(rec["children"]) < 2:
            partner = all_personas.get(rec["partner_id"])
            household_savings = p.wallet_inr + (partner.wallet_inr if partner else 0)
            
            # Opportunity to welcome a child
            if household_savings > 45000.0 and (tick - (rec["wedding_tick"] or 0) >= 3) and random.random() < 0.15:
                child_name = random.choice(CHILD_NAMES) + " " + p.name.split()[-1]
                school = random.choice(SCHOOLS)
                child = {
                    "id": f"child_{p.id}_{len(rec['children'])+1}",
                    "name": child_name,
                    "age": 1,
                    "birth_tick": tick,
                    "parents": [p.name, rec["partner_name"]],
                    "school": school
                }
                rec["children"].append(child)
                p.spend_inr(6000.0, f"Baby shower & nursery celebration for {child_name}")
                rec["happiness"] = 100.0
                
                # Sync partner
                if partner:
                    op_rec = self.register_or_get_citizen(partner)
                    op_rec["children"].append(child)
                    op_rec["happiness"] = 100.0
                    self._persist_citizen(op_rec)
                    
                title = f"BABY BORN: {child_name} welcomed by {p.name} & {rec['partner_name']}!"
                desc = f"Healthy new addition to the Bengaluru metropolis family! Enrolled at {school}."
                self.record_milestone("BIRTH", title, desc, "🍼", tick, f"{p.name} & {rec['partner_name']}")
                events_generated.append(title)

        # 5. TRAVEL, LEISURE OUTINGS & VACATIONS
        if random.random() < 0.08 and (tick - rec["last_vacation_tick"] > 6):
            dest = random.choice(TRAVEL_DESTINATIONS)
            p.spend_inr(dest["cost"], f"Vacation getaway: {dest['name'].replace('_', ' ')}")
            rec["happiness"] = min(100.0, rec["happiness"] + dest["joy"])
            rec["vacation_count"] += 1
            rec["last_vacation_tick"] = tick
            
            title = f"TRAVEL: {p.name} explored {dest['name'].replace('_', ' ')}!"
            desc = f"{dest['desc']}. Spent ₹{int(dest['cost'])}, happiness boosted to {int(rec['happiness'])}%."
            self.record_milestone("VACATION", title, desc, "✈️", tick, p.name)
            events_generated.append(title)

        # 6. ENTREPRENEURSHIP: FOUNDING STARTUPS & BUSINESS EXPANSION
        if rec["company_id"] is None and p.wallet_inr > 40000.0 and random.random() < 0.12:
            s_tmpl = random.choice(STARTUP_TEMPLATES)
            c_name = f"{p.name.split()[0]}'s {s_tmpl['name']}"
            equity_cost = 25000.0
            p.spend_inr(equity_cost, f"Incorporated {c_name} in Bengaluru")
            
            company = {
                "name": c_name,
                "sector": s_tmpl["sector"],
                "founder_id": p.id,
                "founder_name": p.name,
                "valuation_inr": s_tmpl["base_val"],
                "revenue_inr": s_tmpl["base_val"] * s_tmpl["rev_factor"],
                "employees": [p.name],
                "created_tick": tick
            }
            
            with self.lock:
                conn = sqlite3.connect(self.db_path)
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO companies_registry (name, sector, founder_id, founder_name, valuation_inr, quarterly_rev_inr, employees_json, created_tick)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (company["name"], company["sector"], company["founder_id"], company["founder_name"],
                      company["valuation_inr"], company["revenue_inr"], str(company["employees"]), tick))
                c_id = cur.lastrowid
                company["id"] = c_id
                conn.commit()
                conn.close()
                
            self.companies.insert(0, company)
            rec["company_id"] = c_id
            rec["career_level"] = 5
            rec["salary_inr"] += 15000.0  # Founder dividend
            
            title = f"STARTUP LAUNCH: {p.name} founded '{c_name}'!"
            desc = f"Sector: {company['sector']} • Initial Valuation: ₹{company['valuation_inr']/100000:,.1f} Lakhs. High-tech job creator!"
            self.record_milestone("STARTUP_LAUNCH", title, desc, "🚀", tick, p.name)
            events_generated.append(title)

        # 7. WEALTH COMPOUNDING & DOUBLING THE MONEY MILESTONES (2x, 4x, 8x...)
        # Current net worth includes liquid wallet + business equity valuation share
        biz_equity = 0.0
        if rec["company_id"]:
            found_biz = next((c for c in self.companies if c.get("id") == rec["company_id"]), None)
            if found_biz:
                biz_equity = found_biz["valuation_inr"] * 0.65  # 65% founder ownership
                
        total_nw = p.wallet_inr + biz_equity
        rec["current_net_worth"] = total_nw
        
        # Check money doubling multiplier
        init_nw = max(10000.0, rec["initial_net_worth"])
        multiplier = total_nw / init_nw
        expected_doublings = int(math.log2(max(1.0, multiplier)))
        
        if expected_doublings > rec["doubling_count"]:
            rec["doubling_count"] = expected_doublings
            mult_display = f"{2 ** expected_doublings}x"
            title = f"WEALTH MULTIPLIED: {p.name} reached {mult_display} Net Worth!"
            desc = f"Net worth doubled to ₹{int(total_nw):,} (Multiplier: {multiplier:.1f}x from ₹{int(init_nw):,})."
            self.record_milestone("WEALTH_DOUBLED", title, desc, "💰", tick, p.name)
            events_generated.append(title)

        # Persist updated life state
        self._persist_citizen(rec)
        
        return {
            "marital_status": rec["marital_status"],
            "partner_name": rec["partner_name"],
            "children_count": len(rec["children"]),
            "happiness": round(rec["happiness"], 1),
            "net_worth": round(total_nw, 0),
            "doublings": rec["doubling_count"],
            "has_company": bool(rec["company_id"]),
            "events": events_generated
        }

    def step_macro_economy(self, all_personas: Dict[str, Any], tick: int) -> Dict[str, Any]:
        """Calculates exact real-world GDP using GDP = C + I + G + NX."""
        with self.lock:
            # Scaled macro-accounting in Crores (1 Cr = ₹10,000,000)
            # Flow conversion: INR to Crores with urban scaling factor (100 agents model metropolitan velocity)
            flow_c_cr = (self.flow_ledger["consumption_inr"] * 1000.0) / 10000000.0
            flow_i_cr = (self.flow_ledger["investment_inr"] * 1000.0) / 10000000.0
            flow_tax_cr = (self.flow_ledger["tax_collected_inr"] * 1000.0) / 10000000.0

            total_wallets = sum(p.wallet_inr for p in all_personas.values())
            total_corp_val = sum(c["valuation_inr"] for c in self.companies) if self.companies else 150000000.0
            corp_i_cr = (total_corp_val / 10000000.0) * 0.05

            c_cr = round(2150.0 + (total_wallets / 200000.0) + flow_c_cr, 2)
            i_cr = round(980.0 + corp_i_cr + flow_i_cr, 2)
            g_cr = round(420.0 + (flow_tax_cr * 0.8), 2)  # Govt reinvests 80% of tax collections into civic infra
            nx_cr = round(300.0 + (len(self.companies) * 8.5), 2)  # Global tech exports

            total_gdp_cr = round(c_cr + i_cr + g_cr + nx_cr, 2)

            # Real annual equivalent growth rate bounded to realistic macroeconomic ranges
            prev_gdp = self.macro_gdp.get("previous_gdp", 3820.00)
            if prev_gdp <= 0:
                prev_gdp = 3820.00
            raw_growth = ((total_gdp_cr - prev_gdp) / prev_gdp) * 100.0 + 7.8
            growth = round(max(6.5, min(11.5, raw_growth)), 1)

            self.macro_gdp["previous_gdp"] = self.macro_gdp.get("gdp_crores", total_gdp_cr)
            self.macro_gdp["gdp_crores"] = total_gdp_cr
            self.macro_gdp["annual_growth_rate"] = growth
            self.macro_gdp["consumption_c_cr"] = c_cr
            self.macro_gdp["investment_i_cr"] = i_cr
            self.macro_gdp["govt_spending_g_cr"] = g_cr
            self.macro_gdp["net_exports_nx_cr"] = nx_cr
            self.macro_gdp["city_treasury_inr"] += self.flow_ledger["tax_collected_inr"]

            # Reset tick flow ledger for next cycle
            self.flow_ledger = {
                "consumption_inr": 0.0,
                "investment_inr": 0.0,
                "govt_spending_inr": 0.0,
                "tax_collected_inr": 0.0,
                "exports_inr": 0.0
            }
            
            # Log macro ledger periodically
            if tick % 3 == 0:
                conn = sqlite3.connect(self.db_path)
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO macro_economy_ledger (tick, gdp_crores, gdp_growth, consumption_cr, investment_cr, govt_cr, net_exports_cr, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (tick, total_gdp_cr, growth, c_cr, i_cr, g_cr, nx_cr, time.time()))
                conn.commit()
                conn.close()

            # Rank Forbes Top Wealthiest Citizens
            rich_list = []
            for cid, rec in self.citizen_records.items():
                p = all_personas.get(cid)
                if p:
                    rich_list.append({
                        "name": p.name,
                        "role": p.role,
                        "net_worth_inr": int(rec["current_net_worth"]),
                        "wallet_inr": int(p.wallet_inr),
                        "multiplier": f"{rec['current_net_worth'] / max(1.0, rec['initial_net_worth']):.1f}x",
                        "marital_status": rec["marital_status"],
                        "kids": len(rec["children"]),
                        "company": next((c["name"] for c in self.companies if c.get("id") == rec["company_id"]), None)
                    })
            rich_list.sort(key=lambda x: x["net_worth_inr"], reverse=True)
            
            # Families summary
            families = []
            for cid, rec in self.citizen_records.items():
                if rec["marital_status"] == "MARRIED" and rec["partner_name"]:
                    # Avoid duplicates
                    c1, c2 = sorted([rec["citizen_name"], rec["partner_name"]])
                    fam_key = f"{c1} & {c2}"
                    if not any(f["couple"] == fam_key for f in families):
                        families.append({
                            "couple": fam_key,
                            "kids_count": len(rec["children"]),
                            "kids": [c["name"] for c in rec["children"]],
                            "happiness": f"{int(rec['happiness'])}%",
                            "wedding_tick": rec["wedding_tick"]
                        })

            return {
                "macro_gdp": self.macro_gdp,
                "forbes_rich_list": rich_list[:8],
                "active_startups": self.companies[:6],
                "active_families": families[:6],
                "recent_milestones": self.milestones[:8]
            }
