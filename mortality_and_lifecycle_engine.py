"""
Mortality, Aging, Generational Inheritance, and Corporate Bankruptcy Engine
Bengaluru Living Metropolis OS
- Tracks citizen biological age, career tiers, health, and natural retirement/passing
- Manages estate inheritance: wills, passing liquid INR wealth and assets to apprentices/heirs
- Corporate bankruptcy court: liquidates failed startups (runway <= 0), conducts asset auctions, and lays off citizens
"""

import random
import time
from typing import Dict, Any, List, Optional

CAREER_STAGES = ["Junior Apprentice", "Mid-Level Builder", "Senior Architect", "Distinguished Fellow", "Retired Elder"]

class LifecycleAndMortalityEngine:
    def __init__(self):
        self.deceased_citizens: List[Dict[str, Any]] = []
        self.liquidated_startups: List[Dict[str, Any]] = []
        self.inheritance_ledger: List[Dict[str, Any]] = []
        self.last_census_tick = 0

    def step_lifecycle(self, citizens: Dict[str, Any], startups: List[Dict[str, Any]], tick: int) -> Dict[str, Any]:
        """Advance biological aging, handle health risks, estate inheritance, and corporate solvency."""
        events = []
        
        # 1. Company Bankruptcy & Liquidation Check
        for s in startups:
            # Check runway burn
            if s.get("status") == "ACTIVE":
                runway = s.get("runway_months", 12.0)
                # Decrement runway slightly every 8 ticks
                if tick % 8 == 0:
                    runway = max(0.0, runway - 0.4)
                    s["runway_months"] = round(runway, 1)

                if runway <= 0.0:
                    # BANKRUPTCY DECLARED
                    s["status"] = "BANKRUPT_LIQUIDATED"
                    founder_name = s.get("founder", "Unknown Founder")
                    ev = {
                        "type": "COMPANY_BANKRUPTCY",
                        "tick": tick,
                        "company": s.get("name"),
                        "sector": s.get("sector"),
                        "founder": founder_name,
                        "message": f"🚨 [BANKRUPTCY COURT] '{s.get('name')}' ran out of capital (0 months runway). Company liquidated, desks auctioned in Manyata Tech Park."
                    }
                    self.liquidated_startups.append(ev)
                    events.append(ev)

                    # Lay off citizen employees if any
                    for c in citizens.values():
                        if c.role == "Startup Founder" and c.name == founder_name:
                            c.action = "Seeking New Venture Capital after Bankruptcy"
                            c.current_arousal = min(1.0, getattr(c, "current_arousal", getattr(c, "arousal", 0.25)) + 0.35)
                            c.wallet_inr = max(5000.0, c.wallet_inr * 0.4)

        # 2. Citizen Biological Aging & Estate Inheritance
        # Every 20 ticks represents a life progression milestone
        if tick % 20 == 0 and tick > 0:
            for c in citizens.values():
                # Increment biological age metadata
                if not hasattr(c, "biological_age"):
                    c.biological_age = random.randint(22, 68)
                else:
                    c.biological_age += 1

                # Health degradation / recovery based on energy and stress
                if not hasattr(c, "health_score"):
                    c.health_score = 95.0
                
                # High arousal/stress decreases health, rest restores it
                arousal_val = getattr(c, "current_arousal", getattr(c, "arousal", 0.25))
                health_delta = -1.2 if arousal_val > 0.6 else 0.8
                c.health_score = max(10.0, min(100.0, c.health_score + health_delta))

                # Life Milestone: Retirement
                if c.biological_age >= 65 and not getattr(c, "is_retired", False):
                    c.is_retired = True
                    c.role = "Emeritus Tech Fellow & Advisor"
                    c.action = "Advising young founders at Church Street Cafe"
                    events.append({
                        "type": "CITIZEN_RETIREMENT",
                        "tick": tick,
                        "citizen": c.name,
                        "age": c.biological_age,
                        "message": f"🎖️ [LIFECYCLE] {c.name} turned {c.biological_age} and transitioned to Retired Elder status. Mentoring apprentices in Indiranagar."
                    })

                # Mentorship: Senior/Retired citizens mentor apprentices in their department
                if getattr(c, "is_retired", False) or c.biological_age > 50:
                    apprentices = [
                        other for other in citizens.values() 
                        if other.id != c.id and getattr(other, "department", "") == getattr(c, "department", "")
                        and getattr(other, "biological_age", 25) < 35
                    ]
                    if apprentices and random.random() < 0.20:
                        mentee = random.choice(apprentices)
                        mentee.perceive(f"Received career mentorship from {c.name} over filter coffee", stress_impact=-0.05)
                        c.perceive(f"Mentored junior apprentice {mentee.name} on systems craftsmanship", stress_impact=-0.03)
                        events.append({
                            "type": "MENTORSHIP_SESSION",
                            "tick": tick,
                            "mentor": c.name,
                            "mentee": mentee.name,
                            "department": getattr(c, "department", "General"),
                            "message": f"🤝 [MENTORSHIP] {c.name} conducted a career mentorship session with apprentice {mentee.name} ({getattr(c, 'department', '')})."
                        })

                # Generational Succession / Succession Will (Rare event for extreme age/health)
                if c.biological_age >= 80 or c.health_score < 15.0:
                    candidates = [other for other in citizens.values() if other.name != c.name and getattr(other, "biological_age", 30) < 45]
                    if candidates:
                        # Prioritize apprentice in same department
                        dept_candidates = [other for other in candidates if getattr(other, "department", "") == getattr(c, "department", "")]
                        heir = random.choice(dept_candidates) if dept_candidates else random.choice(candidates)
                        
                        inheritance_amount = round(c.wallet_inr * 0.85, 2)
                        c.wallet_inr = round(c.wallet_inr * 0.15, 2)
                        heir.wallet_inr = round(heir.wallet_inr + inheritance_amount, 2)
                        c.health_score = 70.0  # Medical stabilization at Narayana Health Clinic
                        c.biological_age = min(85, c.biological_age) # Dignified senior tenure
                        c.role = f"Emeritus Elder ({getattr(c, 'department', 'General')})"
                        
                        rec = {
                            "type": "ESTATE_INHERITANCE",
                            "tick": tick,
                            "grantor": c.name,
                            "heir": heir.name,
                            "department": getattr(c, "department", ""),
                            "amount_inr": f"₹{inheritance_amount:,.2f}",
                            "message": f"📜 [ESTATE PROBATE] {c.name} executed a generational succession deed transferring ₹{inheritance_amount:,.2f} to apprentice {heir.name}."
                        }
                        self.inheritance_ledger.append(rec)
                        self.deceased_citizens.append({
                            "grantor": c.name,
                            "heir": heir.name,
                            "tick": tick,
                            "inheritance_amount": inheritance_amount
                        })
                        if len(self.inheritance_ledger) > 100:
                            self.inheritance_ledger.pop(0)
                        events.append(rec)

        return {
            "events": events,
            "total_liquidations": len(self.liquidated_startups),
            "recent_liquidations": self.liquidated_startups[-5:],
            "recent_inheritances": self.inheritance_ledger[-5:]
        }

    def get_lifecycle_stats(self) -> Dict[str, Any]:
        return {
            "total_liquidations": len(self.liquidated_startups),
            "recent_liquidations": self.liquidated_startups[-5:],
            "total_inheritances": len(self.inheritance_ledger),
            "recent_inheritances": self.inheritance_ledger[-5:]
        }
