"""
Metropolis Social Media & Community Groups Engine ("Namma-Net")
Simulates:
1. BLR Pulse (X / Twitter clone for 100 autonomous citizens) with live hashtags and quotes.
2. Community Groups (WhatsApp / Discord Guilds for Founders, Heritage, Fellowship, Care).
3. r/bangalore (Interactive Reddit forum with upvoted posts and comments).
4. Citizen Cognitive Tools (Market Viability Scanner, Live Weather Radar, City News Feed).
"""

import time
import random
import json
import sqlite3
import threading
from typing import Dict, List, Any, Optional

DB_PATH = "/Users/lalith/ray_agent_world/world_memory.sqlite"

COMMUNITY_GROUPS = [
    {
        "id": "FOUNDERS_GUILD",
        "name": "🚀 Indiranagar & HSR Founders Guild",
        "category": "TECH_STARTUPS",
        "members_count": 42,
        "icon": "💻",
        "description": "Seed to Series-B founders discussing runway, burn rate, synthetic focus groups & kernel architectures.",
        "channel": "#founders-general",
        "recent_chatter": [
            {"sender": "Aarav Patel", "role": "Kernel Architect", "text": "If you are pricing your developer tool above ₹1,500/mo without flamegraphs, the focus group will destroy you."},
            {"sender": "Priya Sharma", "role": "Design Lead", "text": "Zero-copy UI with sub-16ms latency is the baseline for 2026. Stop adding unneeded frameworks."},
            {"sender": "Vikram Malhotra", "role": "Venture Lead", "text": "Seed valuations are tied directly to customer retention and CAC payback under 6 months."}
        ]
    },
    {
        "id": "TEMPLE_HERITAGE",
        "name": "🛕 Basavanagudi Temple & Heritage Trust",
        "category": "CULTURE_SPIRITUAL",
        "members_count": 28,
        "icon": "🛕",
        "description": "Preserving Bull Temple traditions, morning sufi/carnatic concerts, and heritage darshinis.",
        "channel": "#basavanagudi-circle",
        "recent_chatter": [
            {"sender": "Ananth Murthy", "role": "Darshini Manager", "text": "Kadalekai Parishe preparations starting early this year near Dodda Basavana Gudi."},
            {"sender": "Lakshmi Devi", "role": "Artisan Baker", "text": "Morning butter masala dosa with pure ghee at Vidyarthi Bhavan after 6 AM archana."},
            {"sender": "Suresh Kumar", "role": "Transit Operator", "text": "Special Namma Metro feeder shuttles deployed between National College and Bull Temple."}
        ]
    },
    {
        "id": "CHURCH_FELLOWSHIP",
        "name": "⛪ St. Mark's & Shivajinagar Fellowship",
        "category": "FAITH_COMMUNITY",
        "members_count": 26,
        "icon": "⛪",
        "description": "Sunday choir practice, community food drives, and inter-faith youth initiatives.",
        "channel": "#fellowship-desk",
        "recent_chatter": [
            {"sender": "David Joseph", "role": "Community Organizer", "text": "Sunday morning service at 8:30 AM at St. Mark's Cathedral. All are welcome for the fellowship breakfast."},
            {"sender": "Mary Thomas", "role": "Nurse Lead", "text": "Free blood pressure and health checkups organized at the church hall this Saturday."},
            {"sender": "George Mathew", "role": "Urban Planner", "text": "Peaceful heritage walk scheduled along Cubbon Park and Trinity Church corridor."}
        ]
    },
    {
        "id": "CARE_HEALTH_AID",
        "name": "🏥 Namma Care & Citizen Mutual Aid",
        "category": "HEALTHCARE_AID",
        "members_count": 35,
        "icon": "🏥",
        "description": "Emergency ambulance coordination, mental health circles, child care and wellness clinics.",
        "channel": "#health-dispatch",
        "recent_chatter": [
            {"sender": "Dr. Harish Rao", "role": "Chief Medical Officer", "text": "Narayana Care Clinic in HSR operating 24/7. Monsoon flu vaccines available."},
            {"sender": "Meera Nair", "role": "Child Care Counselor", "text": "Community daycare at Dev Co-Living PG now open for working parents across Manyata & Bagmane."},
            {"sender": "Rohan Sen", "role": "Fitness Coach", "text": "Rest and hydration reminders for everyone working late night hackathons."}
        ]
    },
    {
        "id": "COFFEE_CONNOISSEURS",
        "name": "☕ Bangalore Specialty Coffee Society",
        "category": "FOOD_CULTURE",
        "members_count": 38,
        "icon": "☕",
        "description": "Chicory vs Single-Origin Arabica debates, roastery cupping sessions, and breakfast trails.",
        "channel": "#cupping-table",
        "recent_chatter": [
            {"sender": "Karthik Varma", "role": "Head Barista", "text": "New anaerobic fermentation lot from Chikmagalur just dialed in at Indiranagar 100ft."},
            {"sender": "Sneha Reddy", "role": "Product Manager", "text": "Podi idli followed by a piping hot tumbler of chicory filter coffee is the only true morning fuel."},
            {"sender": "Arjun Somayaji", "role": "Kernel Researcher", "text": "Best place to review PRs: Third Wave Church Street or Brahmin's Coffee Bar?"}
        ]
    }
]

class MetropolisSocialAndCommunity:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self.lock = threading.Lock()
        self.tweets: List[Dict[str, Any]] = []
        self.trending_hashtags: List[Dict[str, Any]] = [
            {"tag": "#SilkBoardGridlock", "tweets_count": 1420, "sentiment": "Sardonic Humorous"},
            {"tag": "#DevPulseTrial", "tweets_count": 980, "sentiment": "Hyper-Skeptical"},
            {"tag": "#FilterCoffeeIndiranagar", "tweets_count": 840, "sentiment": "Enthusiastic"},
            {"tag": "#NammaMetroYellowLine", "tweets_count": 760, "sentiment": "Optimistic"},
            {"tag": "#BullTempleMorning", "tweets_count": 610, "sentiment": "Peaceful Reverent"},
            {"tag": "#DevCoLivingHomes", "tweets_count": 490, "sentiment": "Community Warmth"}
        ]
        self.reddit_threads: List[Dict[str, Any]] = [
            {
                "id": "r_blr_1",
                "title": "PSA: Stop launching ₹2,499 AI wrappers when our median monthly discretionary budget is ₹1,200",
                "author": "u/aarav_kernel",
                "upvotes": 428,
                "comments_count": 86,
                "flair": "Startups & Reality Check",
                "snippet": "The recent synthetic focus group roasted that new SaaS tool. In Bangalore we build with eBPF, SIMD, and open source. If you want our money, show reproducible benchmarks, not VC buzzwords."
            },
            {
                "id": "r_blr_2",
                "title": "Sunday Morning Pilgrimage: Bull Temple Basavanagudi -> Vidyarthi Bhavan Dosa",
                "author": "u/ananth_heritage",
                "upvotes": 512,
                "comments_count": 43,
                "flair": "Namma Ooru Culture",
                "snippet": "Nothing resets the soul after 60-hour sprint weeks like the scent of temple camphor, fresh jasmine, and golden crispy benne dosa."
            },
            {
                "id": "r_blr_3",
                "title": "Dev Co-Living PG rooftop community session was wholesome tonight",
                "author": "u/sneha_pm",
                "upvotes": 319,
                "comments_count": 29,
                "flair": "Living in BLR",
                "snippet": "Engineers, baristas, doctors, and artists sitting together under the stars talking about life in Bangalore. We really built a real metropolis."
            }
        ]
        self._bootstrap_starter_tweets()

    def _bootstrap_starter_tweets(self):
        starter = [
            {"handle": "@aarav_kernel", "name": "Aarav Patel", "badge": "💻 Architect", "text": "If your memory model requires thread locks in 2026, you're leaving 90% of your M4 silicon on the table. POSIX shm is the way.", "likes": 48, "retweets": 12, "time": "5m ago", "tags": ["#Kernel", "#HighPerf"]},
            {"handle": "@priya_ux", "name": "Priya Sharma", "badge": "🎨 Designer", "text": "Church Street petrichor + filter coffee + Figma review. Peak Bangalore aesthetic unlocked. ☕🌧️", "likes": 64, "retweets": 18, "time": "12m ago", "tags": ["#FilterCoffeeIndiranagar", "#BangaloreRains"]},
            {"handle": "@karthik_coffee", "name": "Karthik Varma", "badge": "☕ Barista", "text": "Roasted 40kg of Chikmagalur anaerobic lot today. The chicory ratio is 15% for the authentic Mysore kick.", "likes": 32, "retweets": 5, "time": "18m ago", "tags": ["#FilterCoffeeIndiranagar"]},
            {"handle": "@vikram_vc", "name": "Vikram Malhotra", "badge": "📈 Investor", "text": "Synthetic consumer focus groups have cut our diligence cycle from 3 weeks to 30 seconds. Unvarnished truth is priceless.", "likes": 89, "retweets": 24, "time": "25m ago", "tags": ["#DevPulseTrial", "#Startups"]},
            {"handle": "@sowmya_care", "name": "Sowmya Rao", "badge": "🏥 Care Lead", "text": "Narayana Health Clinic at HSR is hosting free wellness consultations all evening. Take care of your mental stamina!", "likes": 41, "retweets": 9, "time": "30m ago", "tags": ["#NammaCare"]}
        ]
        self.tweets = starter

    def step(self, tick: int, world_time: str, circadian_phase: str, recent_fg_audit: Optional[Dict[str, Any]] = None):
        # Generate new contextual citizen tweet reacting to time or events
        c_names = [
            ("@aarav_kernel", "Aarav Patel", "💻 Architect"),
            ("@priya_ux", "Priya Sharma", "🎨 Designer"),
            ("@karthik_coffee", "Karthik Varma", "☕ Barista"),
            ("@ananth_heritage", "Ananth Murthy", "🛕 Heritage Lead"),
            ("@mary_fellowship", "Mary Thomas", "⛪ Fellowship"),
            ("@dr_harish", "Dr. Harish Rao", "🏥 Medical Officer"),
            ("@sneha_pm", "Sneha Reddy", "📱 Product Manager")
        ]
        author = random.choice(c_names)
        
        if recent_fg_audit and recent_fg_audit.get("summary", {}).get("is_commercial_failure"):
            s = recent_fg_audit["summary"]
            p_name = s.get("target_product", "Product")
            text = f"Just saw the brutal focus group autopsy on '{p_name}'. 100 personas called out the pricing fantasy immediately. Listen to real customers! #DevPulseTrial"
            tag = "#DevPulseTrial"
        elif "Midnight" in circadian_phase:
            text = "01:00 AM at Dev Co-Living PG. Compiling C-aligned CRDTs while the city sleeps. The air is so quiet and crisp at 15°C. #MidnightCompile"
            tag = "#MidnightCompile"
        elif "Dawn" in circadian_phase or "Early Morning" in circadian_phase:
            text = "Brahmamuhurtha dawn at Bull Temple Basavanagudi. Bells ringing, mist clearing over Lalbagh. Time for morning prayer. #BullTempleMorning"
            tag = "#BullTempleMorning"
        elif "Afternoon" in circadian_phase:
            text = "Midday sprint huddle wrapped. Grabbed lunch at Church Street terrace. Silk Board is living up to its gridlock reputation today! #SilkBoardGridlock"
            tag = "#SilkBoardGridlock"
        else:
            text = "Evening gathering at St. Mark's community garden. Good conversations about building long-term social trust in Bengaluru. #NammaOoru"
            tag = "#NammaOoru"

        new_tweet = {
            "handle": author[0],
            "name": author[1],
            "badge": author[2],
            "text": text,
            "likes": random.randint(12, 120),
            "retweets": random.randint(3, 35),
            "time": "Just now",
            "tags": [tag]
        }
        self.tweets.insert(0, new_tweet)
        if len(self.tweets) > 25:
            self.tweets = self.tweets[:25]

    def post_user_tweet(self, text: str, handle: str = "@Governor_Lalith", name: str = "Lalith (Governor)") -> Dict[str, Any]:
        t = {
            "handle": handle,
            "name": name,
            "badge": "⚡ CITY GOVERNOR",
            "text": text,
            "likes": 154,
            "retweets": 48,
            "time": "Just now",
            "tags": ["#GovernorDirective", "#BengaluruMetropolis"]
        }
        self.tweets.insert(0, t)
        return t

    def get_social_state(self) -> Dict[str, Any]:
        return {
            "tweets": self.tweets[:12],
            "trending_hashtags": self.trending_hashtags,
            "community_groups": COMMUNITY_GROUPS,
            "reddit_threads": self.reddit_threads
        }

SOCIAL_OS = MetropolisSocialAndCommunity()
