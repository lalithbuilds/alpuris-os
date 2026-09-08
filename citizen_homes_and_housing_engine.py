"""
Dedicated Citizen Homes & Residential Housing Engine
Bengaluru Living Metropolis OS
- Assigns all 100 citizens permanent, authentic dedicated homes across Bengaluru sectors
- Tracks residential leases, monthly rent/mortgage payments, home furnishings, and night sleep cycles
- Manages physical commute between workplace and home during evening/night circadian phases
"""

import random
from typing import Dict, Any, List, Optional

RESIDENTIAL_COMMUNITIES = [
    {
        "community_name": "Dev Co-Living PG & Tech Pods",
        "zone": "Indiranagar_100ft_Startups",
        "type": "Co-Living PG & Pods",
        "address": "12th Main Road, HAL 2nd Stage, Indiranagar",
        "median_rent": 16500.0,
        "units": [
            "Flat 101", "Flat 102", "Flat 103", "Flat 201", "Flat 202", "Flat 203", 
            "Flat 301", "Flat 302", "Flat 303", "Penthouse 401", "Penthouse 402",
            "Rooftop Pod A", "Rooftop Pod B", "Rooftop Pod C", "Rooftop Pod D"
        ]
    },
    {
        "community_name": "Sobha Daisy & Carnation Enclave",
        "zone": "HSR_Layout_Residences",
        "type": "Gated Society Apartment",
        "address": "27th Main, Sector 1, HSR Layout",
        "median_rent": 28000.0,
        "units": [
            "Tower A - 101", "Tower A - 202", "Tower A - 302", "Tower A - 404", "Tower A - 501",
            "Tower B - 101", "Tower B - 203", "Tower B - 304", "Tower B - 502", "Tower B - 601",
            "Tower C - 102", "Tower C - 203", "Tower C - 401", "Tower C - 601", "Tower D - 702"
        ]
    },
    {
        "community_name": "Basavanagudi Traditional Heritage Houses",
        "zone": "Gandhi_Bazaar_Heritage",
        "type": "Heritage Independent House",
        "address": "Bull Temple Road, Basavanagudi",
        "median_rent": 19000.0,
        "units": [
            "House #14 'Ananda Nilaya'", "House #18 'Prashanti'", "House #22 'Guru Kripa'", 
            "House #27 'Srinidhi'", "House #33 'Sharada Krupa'", "House #38 'Shanti Nivas'", 
            "House #41 'Varuna'", "House #45 'Cauvery Illa'", "House #49 'Ganga Kutir'", 
            "House #51 'Venkateshwara Kuteera'", "House #55 'Amrutha'", "House #60 'Vijayanagar Illa'",
            "House #65 'Saraswathi'", "House #70 'Kailasa'", "House #75 'Chitrakoot'"
        ]
    },
    {
        "community_name": "Prestige Ozone & Windmills Villas",
        "zone": "Whitefield_ITPB",
        "type": "Luxury Tech Villa",
        "address": "Varthur Road, Whitefield",
        "median_rent": 48000.0,
        "units": [
            "Villa 12 'The Banyan'", "Villa 15 'The Teak'", "Villa 18 'The Cedar'", 
            "Villa 21 'The Gulmohar'", "Villa 25 'The Palms'", "Villa 28 'The Magnolia'", 
            "Villa 31 'The Orchard'", "Villa 35 'The Jacaranda'", "Villa 39 'The Willow'", 
            "Villa 42 'Cyber Crest'", "Villa 45 'Silicon Vista'", "Villa 48 'Cloud Crest'",
            "Villa 52 'Horizon Point'", "Villa 55 'Green Gable'", "Villa 60 'Summit Villa'"
        ]
    },
    {
        "community_name": "Manyata Cloud Residency Towers",
        "zone": "Manyata_Tech_Park",
        "type": "Modern High-Rise",
        "address": "Nagavara Outer Ring Road",
        "median_rent": 22000.0,
        "units": [
            "Tower 1 - 102", "Tower 1 - 204", "Tower 1 - 306", "Tower 1 - 508", "Tower 1 - 702",
            "Tower 2 - 101", "Tower 2 - 205", "Tower 2 - 312", "Tower 2 - 501", "Tower 2 - 802",
            "Tower 3 - 202", "Tower 3 - 401", "Tower 3 - 603", "Tower 3 - 805", "Tower 3 - 905"
        ]
    },
    {
        "community_name": "Koramangala 4th Block Garden Suites",
        "zone": "Koramangala_Microbrewery_Pub",
        "type": "Boutique Studio Suite",
        "address": "80 Feet Road, 4th Block, Koramangala",
        "median_rent": 26000.0,
        "units": [
            "Suite 1A", "Suite 1B", "Suite 2A", "Suite 2B", "Suite 3A", "Suite 3B", 
            "Suite 4A", "Suite 4B", "Suite 4C", "Studio 10", "Studio 12", "Studio 14", 
            "Studio 15", "Studio 18", "Studio 20"
        ]
    },
    {
        "community_name": "Shivajinagar & St. Mark's Parish Homes",
        "zone": "MG_Road_Boulevard",
        "type": "Colonial Anglo-Indian Townhouse",
        "address": "Seppings Road, Shivajinagar",
        "median_rent": 18000.0,
        "units": [
            "Townhouse 4", "Townhouse 8", "Townhouse 11", "Townhouse 14", "Townhouse 17", 
            "Townhouse 21", "Townhouse 25", "Flat 1 - St. Mark's Close", "Flat 3 - St. Mark's Close", 
            "Flat 5 - Rose Lane", "Flat 7 - Rose Lane", "Flat 9 - Rose Lane", 
            "Parish Cottage A", "Parish Cottage B", "Parish Cottage C"
        ]
    },
    {
        "community_name": "Electronic City Cyber Meadows",
        "zone": "Electronic_City_Phase1",
        "type": "Suburban Tech Complex",
        "address": "Hosur Main Road, Phase 1",
        "median_rent": 14000.0,
        "units": [
            "Block E1 - 102", "Block E1 - 201", "Block E1 - 304", "Block E1 - 402", "Block E1 - 501",
            "Block E2 - 101", "Block E2 - 201", "Block E2 - 303", "Block E2 - 405", "Block E2 - 502",
            "Block E3 - 104", "Block E3 - 202", "Block E3 - 303", "Block E3 - 401", "Block E3 - 505"
        ]
    }
]

class CitizenHousingEngine:
    def __init__(self):
        # citizen_id -> home_details
        self.citizen_homes: Dict[str, Dict[str, Any]] = {}
        self.total_rent_collected_inr = 0.0
        self.sleep_states: Dict[str, bool] = {}

    def assign_homes_to_citizens(self, citizens: Dict[str, Any]):
        """Assign every citizen an authentic, workplace-aligned permanent home in Bengaluru."""
        # Workplace zone to residential community preference mapping
        zone_home_preference = {
            "Manyata_Tech_Park": "Manyata Cloud Residency Towers",
            "IISc_Research_Campus": "Basavanagudi Traditional Heritage Houses",
            "Indiranagar_100ft_Startups": "Dev Co-Living PG & Tech Pods",
            "Whitefield_ITPB": "Prestige Ozone & Windmills Villas",
            "Electronic_City_Phase_1": "Electronic City Cyber Meadows",
            "Electronic_City_Phase1": "Electronic City Cyber Meadows",
            "Koramangala_Microbrewery_Pub": "Koramangala 4th Block Garden Suites",
            "Nexus_Koramangala_Mall": "Koramangala 4th Block Garden Suites",
            "Silk_Board_Junction": "Sobha Daisy & Carnation Enclave",
            "Cubbon_Park_Canopy": "Shivajinagar & St. Mark's Parish Homes",
            "Vidhana_Soudha_Capitol": "Shivajinagar & St. Mark's Parish Homes",
            "MG_Road_Boulevard": "Shivajinagar & St. Mark's Parish Homes",
            "Church_Street_Cafes": "Shivajinagar & St. Mark's Parish Homes"
        }

        community_lookup = {c["community_name"]: c for c in RESIDENTIAL_COMMUNITIES}
        allocated_unit_counts: Dict[str, int] = {c["community_name"]: 0 for c in RESIDENTIAL_COMMUNITIES}
        
        for c in citizens.values():
            if c.id in self.citizen_homes:
                continue

            # Prioritize matching home zone to citizen workplace
            pref_name = zone_home_preference.get(getattr(c, "location", ""), "Sobha Daisy & Carnation Enclave")
            comm = community_lookup.get(pref_name, RESIDENTIAL_COMMUNITIES[0])
            
            # If preferred community is full, pick next available community
            if allocated_unit_counts[comm["community_name"]] >= len(comm["units"]):
                for alt_comm in RESIDENTIAL_COMMUNITIES:
                    if allocated_unit_counts[alt_comm["community_name"]] < len(alt_comm["units"]):
                        comm = alt_comm
                        break

            u_idx = allocated_unit_counts[comm["community_name"]]
            unit_name = comm["units"][u_idx % len(comm["units"])]
            allocated_unit_counts[comm["community_name"]] += 1

            rent = round(comm["median_rent"] * random.uniform(0.90, 1.10), 2)
            # Homeownership aligned with career seniority and wealth
            is_senior = hasattr(c, "biological_age") and c.biological_age > 45
            has_capital = getattr(c, "wallet_inr", 25000.0) > 60000.0
            is_homeowner = (is_senior and has_capital and random.random() < 0.40)

            home_record = {
                "citizen_id": c.id,
                "citizen_name": c.name,
                "community_name": comm["community_name"],
                "housing_type": comm["type"],
                "zone": comm["zone"],
                "full_address": f"{unit_name}, {comm['community_name']}, {comm['address']}, Bengaluru",
                "monthly_rent_inr": 0.0 if is_homeowner else rent,
                "room_furnishings": [
                    "Ergonomic Standing Desk", 
                    "Orthopedic Memory Foam Bed", 
                    "Filter Coffee French Press", 
                    "High-Speed Fiber Router (1 Gbps)", 
                    "Bengaluru Monsoon Umbrella Stand"
                ],
                "roommates": [],
                "is_owner": is_homeowner,
                "current_occupancy": "VACANT"
            }
            self.citizen_homes[c.id] = home_record
            c.home_zone = comm["zone"]
            self.sleep_states[c.id] = False

    def sync_married_cohabitation(self, citizen_id_1: str, citizen_id_2: str, citizens: Dict[str, Any]):
        """Establish joint co-living household for married citizen couples."""
        h1 = self.citizen_homes.get(citizen_id_1)
        h2 = self.citizen_homes.get(citizen_id_2)
        c1 = citizens.get(citizen_id_1)
        c2 = citizens.get(citizen_id_2)
        if h1 and h2 and c1 and c2:
            # Combine into primary residence
            joint_home = h1
            h2["full_address"] = joint_home["full_address"]
            h2["community_name"] = joint_home["community_name"]
            h2["zone"] = joint_home["zone"]
            c2.home_zone = joint_home["zone"]
            
            if c2.name not in joint_home["roommates"]:
                joint_home["roommates"].append(c2.name)
            if c1.name not in h2["roommates"]:
                h2["roommates"].append(c1.name)

    def step_circadian_residence(self, citizens: Dict[str, Any], circadian_phase_cat: str, tick: int) -> Dict[str, Any]:
        """Update whether citizens are home sleeping or out at work based on circadian phase."""
        sleeping_count = 0
        at_home_count = 0
        events = []

        is_night_or_sleep = circadian_phase_cat in ["NIGHT", "MIDNIGHT", "EARLY_MORNING"]

        for c in citizens.values():
            home = self.citizen_homes.get(c.id)
            if not home:
                continue

            if is_night_or_sleep:
                # Citizens commute home, sleep, recharge energy and relieve stress
                c.location = home["zone"]
                self.sleep_states[c.id] = True
                home["current_occupancy"] = "SLEEPING_IN_BED"
                sleeping_count += 1
                at_home_count += 1
                
                # Restore energy and reduce arousal/stress during sleep
                c.energy = min(100.0, c.energy + 10.0)
                if hasattr(c, "current_arousal"):
                    c.current_arousal = max(0.10, c.current_arousal - 0.04)
                elif hasattr(c, "arousal"):
                    c.arousal = max(0.10, c.arousal - 0.04)

                c.action = f"Sleeping at home in {home['community_name']} ({home['housing_type']})"
                c.last_action = c.action
                c.current_task = f"Asleep in {home['full_address'][:30]}..."
            else:
                self.sleep_states[c.id] = False
                home["current_occupancy"] = "AWAY_AT_WORK"
                # Natural energy drain during work
                c.energy = max(15.0, c.energy - 2.0)

            # Monthly rent deduction every 60 ticks
            if tick % 60 == 0 and tick > 0 and not home["is_owner"]:
                rent_due = home["monthly_rent_inr"]
                if c.wallet_inr >= rent_due:
                    c.wallet_inr = round(c.wallet_inr - rent_due, 2)
                    self.total_rent_collected_inr += rent_due
                    events.append({
                        "citizen": c.name,
                        "amount": rent_due,
                        "message": f"🏠 [RENT PAYMENT] {c.name} paid ₹{rent_due:,.2f} monthly rent for {home['full_address']}."
                    })

        return {
            "total_houses_assigned": len(self.citizen_homes),
            "citizens_at_home": at_home_count,
            "citizens_sleeping": sleeping_count,
            "total_rent_collected_inr": f"₹{self.total_rent_collected_inr:,.2f}",
            "recent_housing_events": events[-5:]
        }

    def get_citizen_home(self, citizen_id: str) -> Optional[Dict[str, Any]]:
        return self.citizen_homes.get(citizen_id)
