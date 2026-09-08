"""
Urban Fauna (Street Dogs & Cats) & Living Parks Engine
Bengaluru Living Metropolis OS
- Simulates named Bengaluru Indie street dogs, pet dogs, and rooftop cats roaming sectors
- Manages lush city parks (Cubbon Park, Lalbagh, Agara Lake Promenade)
- Interactive feeding & petting: citizens interacting with animals reduces stress/arousal index
"""

import random
from typing import Dict, Any, List, Optional

NAMED_STREET_DOGS = [
    {
        "id": "DOG_01",
        "name": "Tommy of Church Street",
        "breed": "Indie / Desi Community Dog",
        "color": "Tan & White Coat",
        "zone": "Church_Street_Cafes",
        "favorite_spot": "Outside Blossom Book House & Artisan Cafe",
        "personality": "Gentle, friendly with software engineers, loves Marie Gold biscuits",
        "happiness": 92.0,
        "hunger": 25.0
    },
    {
        "id": "DOG_02",
        "name": "Kaalu of Silk Board",
        "breed": "Black Indie Canine",
        "color": "Jet Black Coat",
        "zone": "Silk_Board_Junction",
        "favorite_spot": "Under Metro Pillar 42 shade",
        "personality": "Street-smart, observes traffic gridlocks calmly",
        "happiness": 84.0,
        "hunger": 30.0
    },
    {
        "id": "DOG_03",
        "name": "Sheru of Indiranagar",
        "breed": "Golden Indie Shepherd",
        "color": "Golden Honey",
        "zone": "Indiranagar_100ft_Startups",
        "favorite_spot": "Dev Co-Living PG entrance porch",
        "personality": "Affectionate, greets founders returning from pitch meetings",
        "happiness": 95.0,
        "hunger": 18.0
    },
    {
        "id": "DOG_04",
        "name": "Rocky of Koramangala",
        "breed": "Spotted Indie Terrier",
        "color": "White with Brown Patches",
        "zone": "Koramangala_Microbrewery_Pub",
        "favorite_spot": "Near outdoor microbrewery beer garden benches",
        "personality": "High-energy, wags tail for pub snacks and patting",
        "happiness": 90.0,
        "hunger": 20.0
    },
    {
        "id": "DOG_05",
        "name": "Chinnu of Basavanagudi",
        "breed": "Heritage Desi Hound",
        "color": "Caramel Fawn",
        "zone": "Gandhi_Bazaar_Heritage",
        "favorite_spot": "Dodda Basavana Gudi (Bull Temple) outer courtyard",
        "personality": "Peaceful temple dog, receives blessings and flower garlands",
        "happiness": 98.0,
        "hunger": 12.0
    }
]

NAMED_URBAN_CATS = [
    {
        "id": "CAT_01",
        "name": "Mimi of Dev PG",
        "breed": "Calico Domestic Shorthair",
        "zone": "Indiranagar_100ft_Startups",
        "favorite_spot": "Rooftop pergola terracotta tiles",
        "personality": "Aloof, loves purring on warm laptop chargers",
        "happiness": 94.0
    },
    {
        "id": "CAT_02",
        "name": "Bella of Church Street",
        "breed": "Grey Striped Tabby",
        "zone": "Church_Street_Cafes",
        "favorite_spot": "Wooden staircase of vintage cafe",
        "personality": "Sunbaths during morning coffee hours, chases park butterflies",
        "happiness": 89.0
    }
]

BENGALURU_PARKS = [
    {
        "park_name": "Cubbon Park Central Sanctuary",
        "zone": "Cubbon_Park_Canopy",
        "features": ["Bamboo Groves", "Lotus Fountain", "King George Statue", "Canine Play Area", "Lush Lawn Canopy"],
        "ambient_activity": "Software architects jogging, golden retrievers playing fetch, morning yoga under eucalyptus trees"
    },
    {
        "park_name": "Lalbagh Botanical Gardens & Lake",
        "zone": "Gandhi_Bazaar_Heritage",
        "features": ["Victorian Glass House", "Peninsular Gneiss Rock", "Lotus Lake Promenade", "Centuries-Old Bonsai"],
        "ambient_activity": "Elders walking with walking sticks, botanists studying rare flora, morning mist over the lake"
    },
    {
        "park_name": "Agara Lake Park Promenade",
        "zone": "HSR_Layout_Residences",
        "features": ["3.2km Running Track", "Lakeside Sunset Benches", "Open-Air Calisthenics Gym", "Duck Pond"],
        "ambient_activity": "Fitness enthusiasts doing pull-ups, families watching painted storks and kingfishers"
    }
]

class UrbanFaunaAndParksEngine:
    def __init__(self):
        self.dogs = [dict(d) for d in NAMED_STREET_DOGS]
        self.cats = [dict(c) for c in NAMED_URBAN_CATS]
        self.parks = list(BENGALURU_PARKS)
        self.recent_interactions: List[Dict[str, Any]] = []

    def step_fauna(self, citizens: Dict[str, Any], tick: int) -> Dict[str, Any]:
        """Simulate autonomous dog/cat movements and friendly citizen petting encounters."""
        new_interactions = []

        # Dogs wander slightly and can be petted by nearby citizens
        for dog in self.dogs:
            # Check if any citizen is in the same zone
            nearby = [c for c in citizens.values() if c.location == dog["zone"]]
            if nearby and random.random() < 0.35:
                citizen = random.choice(nearby)
                # Petting lowers stress and increases energy
                if hasattr(citizen, "current_arousal"):
                    citizen.current_arousal = max(0.1, citizen.current_arousal - 0.20)
                elif hasattr(citizen, "arousal"):
                    citizen.arousal = max(0.1, citizen.arousal - 0.20)
                citizen.energy = min(100.0, citizen.energy + 8.0)
                citizen.last_action = f"Petted indie dog {dog['name']} at {dog['zone']}"
                dog["happiness"] = min(100.0, dog["happiness"] + 4.0)
                
                interaction = {
                    "tick": tick,
                    "dog_name": dog["name"],
                    "citizen": citizen.name,
                    "zone": dog["zone"],
                    "message": f"🐕 [PETTING MOMENT] {citizen.name} stopped to pet {dog['name']} at {dog['zone']}. Stress dropped by 20%!"
                }
                new_interactions.append(interaction)
                self.recent_interactions.append(interaction)

        # Cats purr and relax
        for cat in self.cats:
            cat["happiness"] = min(100.0, cat["happiness"] + 1.0)

        return {
            "total_dogs": len(self.dogs),
            "total_cats": len(self.cats),
            "total_parks": len(self.parks),
            "recent_petting_moments": self.recent_interactions[-5:],
            "dogs": self.dogs,
            "cats": self.cats,
            "parks": self.parks
        }

    def interact_with_fauna(self, citizen_name: str, animal_id: str, action: str = "PET") -> Dict[str, Any]:
        """Manually trigger a petting or feeding interaction."""
        target = next((d for d in self.dogs if d["id"] == animal_id), None)
        if not target:
            target = next((c for c in self.cats if c["id"] == animal_id), None)
        if not target:
            target = self.dogs[0]

        target["happiness"] = min(100.0, target["happiness"] + 10.0)
        return {
            "status": "SUCCESS",
            "animal": target["name"],
            "action": action,
            "message": f"✨ {citizen_name} gave {target['name']} a loving pat and biscuits! Wags tail with joy."
        }
