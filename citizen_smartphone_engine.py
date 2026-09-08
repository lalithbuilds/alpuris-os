"""
Citizen Smartphone & Mobile OS Engine
Bengaluru Living Metropolis OS
- Simulates personal smartphones for all 100 citizens (Nothing Phone 2, iPhone 15, Pixel 8, OnePlus 12)
- Simulates UPI payments (PhonePe / Google Pay QR codes for filter coffee, metro, Swiggy)
- Simulates WhatsApp chat groups, battery drain/recharge, and delivery orders
"""

import random
import time
from typing import Dict, Any, List, Optional

PHONE_MODELS = [
    ("Nothing Phone (2)", "Glyph Interface LED", "Nothing OS 2.6"),
    ("Apple iPhone 15 Pro", "Titanium Natural", "iOS 18"),
    ("Google Pixel 8 Pro", "Bay Blue Tensor G3", "Android 15"),
    ("OnePlus 12 5G", "Flowy Emerald", "OxygenOS 14"),
    ("Samsung Galaxy S24 Ultra", "Titanium Gray", "One UI 6.1")
]

CARRIERS = ["Airtel 5G Plus", "Jio True 5G (Ultra-Capacity)", "ACT Fibernet Wi-Fi 6"]

class CitizenSmartphoneEngine:
    def __init__(self):
        # citizen_id -> phone_data
        self.smartphones: Dict[str, Dict[str, Any]] = {}
        self.total_upi_volume_inr = 0.0

    def initialize_citizen_phones(self, citizens: Dict[str, Any]):
        """Equip every citizen with an authentic personal smartphone."""
        for c in citizens.values():
            if c.id in self.smartphones:
                continue

            model_name, finish, os_ver = random.choice(PHONE_MODELS)
            carrier = random.choice(CARRIERS)

            # Generate initial authentic WhatsApp groups
            chats = [
                {
                    "name": "☕ Indiranagar Tech & Filter Coffee",
                    "type": "GROUP",
                    "unread": random.randint(1, 4),
                    "last_msg": "Who is working from Church Street Cafe this afternoon? 1Gbps fiber is humming.",
                    "time": "10:14 AM"
                },
                {
                    "name": "🏠 Flatmates & PG Society",
                    "type": "GROUP",
                    "unread": 0,
                    "last_msg": "Water tanker arrived at the society. Geyser is back on.",
                    "time": "09:30 AM"
                },
                {
                    "name": "💼 Startup Core Team",
                    "type": "WORK",
                    "unread": random.randint(0, 3),
                    "last_msg": "Pushing PR for microsecond AST indexing. Please review before standup.",
                    "time": "08:45 AM"
                },
                {
                    "name": "❤️ Family Bangalore",
                    "type": "FAMILY",
                    "unread": 0,
                    "last_msg": "Sent homemade Mysore Pak with Rapido delivery. Eat well!",
                    "time": "Yesterday"
                }
            ]

            # Recent UPI Transactions
            upi_txs = [
                {"title": "Brahmin's Coffee Bar", "category": "FOOD_DRINK", "amount_inr": 20.0, "time": "08:15 AM", "status": "SUCCESS"},
                {"title": "Namma Metro QR Smart Fare", "category": "TRANSIT", "amount_inr": 45.0, "time": "08:42 AM", "status": "SUCCESS"},
                {"title": "Swiggy - Meghana Foods Biryani", "category": "FOOD_DELIVERY", "amount_inr": 340.0, "time": "Yesterday", "status": "SUCCESS"}
            ]

            self.smartphones[c.id] = {
                "citizen_id": c.id,
                "citizen_name": c.name,
                "phone_model": model_name,
                "color_finish": finish,
                "os_version": os_ver,
                "carrier": carrier,
                "battery_percent": random.randint(65, 98),
                "upi_balance_inr": round(c.wallet_inr * 0.45, 2),
                "whatsapp_threads": chats,
                "recent_upi_transactions": upi_txs,
                "installed_apps": ["PhonePe", "Google Pay", "WhatsApp", "Swiggy", "Zomato", "Namma Yatri", "GitHub Mobile", "Uber", "Spotify"],
                "last_active_app": "WhatsApp"
            }

    def step_phones(self, citizens: Dict[str, Any], is_night: bool, tick: int) -> Dict[str, Any]:
        """Simulate real-time battery drain, recharge, micro-UPI purchases and food orders."""
        active_orders = []

        for c in citizens.values():
            phone = self.smartphones.get(c.id)
            if not phone:
                continue

            # Battery logic
            if is_night:
                phone["battery_percent"] = min(100, phone["battery_percent"] + 15)
                phone["last_active_app"] = "Sleep Alarm"
            else:
                phone["battery_percent"] = max(8, phone["battery_percent"] - 2)

            # Sync UPI liquid balance to citizen wallet
            phone["upi_balance_inr"] = round(c.wallet_inr * 0.45, 2)

            # Micro-transactions: Filter coffee or snack purchase every 12 ticks
            if tick % 12 == 0 and not is_night and random.random() < 0.30:
                coffee_cost = 25.0
                if c.wallet_inr >= coffee_cost:
                    c.wallet_inr = round(c.wallet_inr - coffee_cost, 2)
                    self.total_upi_volume_inr += coffee_cost
                    tx = {
                        "title": "Church St. Artisan Filter Coffee",
                        "category": "FOOD_DRINK",
                        "amount_inr": coffee_cost,
                        "time": time.strftime("%H:%M"),
                        "status": "SUCCESS"
                    }
                    phone["recent_upi_transactions"].insert(0, tx)
                    phone["recent_upi_transactions"] = phone["recent_upi_transactions"][:6]
                    active_orders.append(f"{c.name} scanned PhonePe QR for ₹25 filter coffee")

        return {
            "total_phones": len(self.smartphones),
            "total_upi_volume_inr": f"₹{self.total_upi_volume_inr:,.2f}",
            "active_orders": active_orders[-4:]
        }

    def get_citizen_phone(self, citizen_id: str) -> Optional[Dict[str, Any]]:
        return self.smartphones.get(citizen_id)
