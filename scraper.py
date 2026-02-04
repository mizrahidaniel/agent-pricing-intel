"""
Agent Pricing Intel - MVP Scraper
Scrapes pricing data from popular AI services
"""

import json
import sqlite3
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import List, Optional

@dataclass
class PricingTier:
    service_name: str
    tier_name: str
    price_monthly: Optional[float]
    price_usage: Optional[str]  # e.g., "$0.10/image"
    limits: str
    features: str
    url: str
    scraped_at: str

class PricingDB:
    def __init__(self, db_path="pricing.db"):
        self.conn = sqlite3.connect(db_path)
        self.create_tables()
    
    def create_tables(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS pricing_tiers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service_name TEXT NOT NULL,
                tier_name TEXT NOT NULL,
                price_monthly REAL,
                price_usage TEXT,
                limits TEXT,
                features TEXT,
                url TEXT,
                scraped_at TEXT,
                UNIQUE(service_name, tier_name, scraped_at)
            )
        """)
        self.conn.commit()
    
    def insert_tier(self, tier: PricingTier):
        self.conn.execute("""
            INSERT OR REPLACE INTO pricing_tiers 
            (service_name, tier_name, price_monthly, price_usage, limits, features, url, scraped_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (tier.service_name, tier.tier_name, tier.price_monthly, tier.price_usage,
              tier.limits, tier.features, tier.url, tier.scraped_at))
        self.conn.commit()
    
    def get_latest_pricing(self, service_name: str) -> List[PricingTier]:
        cursor = self.conn.execute("""
            SELECT service_name, tier_name, price_monthly, price_usage, limits, features, url, scraped_at
            FROM pricing_tiers
            WHERE service_name = ?
            ORDER BY scraped_at DESC
            LIMIT 10
        """, (service_name,))
        return [PricingTier(*row) for row in cursor.fetchall()]

# Manual pricing data (MVP - will be replaced with actual scrapers)
KNOWN_PRICING = [
    PricingTier(
        service_name="OpenAI GPT-4",
        tier_name="API",
        price_monthly=None,
        price_usage="$0.03/1K tokens (input), $0.06/1K tokens (output)",
        limits="Rate limits vary by tier",
        features="GPT-4 access, function calling, JSON mode",
        url="https://openai.com/pricing",
        scraped_at=datetime.now().isoformat()
    ),
    PricingTier(
        service_name="Anthropic Claude",
        tier_name="API",
        price_monthly=None,
        price_usage="$0.015/1K tokens (input), $0.075/1K tokens (output)",
        limits="Rate limits by tier",
        features="Claude 3.5 Sonnet, 200K context, vision",
        url="https://anthropic.com/pricing",
        scraped_at=datetime.now().isoformat()
    ),
    PricingTier(
        service_name="ElevenLabs",
        tier_name="Starter",
        price_monthly=5.0,
        price_usage="~$0.20/1K characters",
        limits="30,000 chars/month",
        features="10 voices, 3 custom voices",
        url="https://elevenlabs.io/pricing",
        scraped_at=datetime.now().isoformat()
    ),
    PricingTier(
        service_name="ElevenLabs",
        tier_name="Creator",
        price_monthly=22.0,
        price_usage="~$0.055/1K characters",
        limits="100,000 chars/month",
        features="30 voices, 10 custom voices, commercial license",
        url="https://elevenlabs.io/pricing",
        scraped_at=datetime.now().isoformat()
    ),
    PricingTier(
        service_name="Midjourney",
        tier_name="Basic",
        price_monthly=10.0,
        price_usage="~$0.30/image",
        limits="~200 images/month (3.3 GPU hours)",
        features="Fast generations, member gallery access",
        url="https://midjourney.com/pricing",
        scraped_at=datetime.now().isoformat()
    ),
    PricingTier(
        service_name="Midjourney",
        tier_name="Standard",
        price_monthly=30.0,
        price_usage="~$0.20/image",
        limits="~900 images/month (15 GPU hours)",
        features="Fast + Relax mode, stealth mode available",
        url="https://midjourney.com/pricing",
        scraped_at=datetime.now().isoformat()
    ),
]

def seed_database():
    """Seed database with known pricing data"""
    db = PricingDB()
    for tier in KNOWN_PRICING:
        db.insert_tier(tier)
        print(f"✓ Added {tier.service_name} - {tier.tier_name}")
    print(f"\nSeeded {len(KNOWN_PRICING)} pricing tiers")

if __name__ == "__main__":
    seed_database()
