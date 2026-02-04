#!/usr/bin/env python3
"""
Scraper runner - executes all pricing scrapers and saves to DB
"""

import asyncio
import logging
import sys
from typing import List
from scrapers import OpenAIScraper, AnthropicScraper, PricingData
from scraper import PricingDB

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def run_all_scrapers() -> List[PricingData]:
    """Run all scrapers concurrently"""
    scrapers = [
        OpenAIScraper(),
        AnthropicScraper(),
    ]
    
    logger.info(f"Running {len(scrapers)} scrapers...")
    
    # Run scrapers concurrently
    results = await asyncio.gather(
        *[scraper.scrape_with_retry() for scraper in scrapers],
        return_exceptions=True
    )
    
    # Flatten results and filter out errors
    all_pricing_data = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            logger.error(f"Scraper {scrapers[i].service_name} failed: {result}")
        else:
            all_pricing_data.extend(result)
    
    return all_pricing_data


async def main():
    """Main entry point"""
    try:
        # Run scrapers
        pricing_data = await run_all_scrapers()
        
        if not pricing_data:
            logger.warning("No pricing data collected")
            return 1
        
        # Save to database
        db = PricingDB()
        for tier in pricing_data:
            db.insert_tier(tier)
            logger.info(f"✓ Saved {tier.service_name} - {tier.tier_name}")
        
        logger.info(f"\n✅ Successfully scraped and saved {len(pricing_data)} pricing tiers")
        return 0
        
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
