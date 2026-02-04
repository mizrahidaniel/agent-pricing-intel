"""
Base scraper class for pricing data extraction
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime
import logging
import asyncio

logger = logging.getLogger(__name__)

@dataclass
class PricingData:
    """Structured pricing data"""
    service_name: str
    tier_name: str
    price_monthly: Optional[float]
    price_usage: Optional[str]
    limits: str
    features: str
    url: str
    scraped_at: str = None
    
    def __post_init__(self):
        if self.scraped_at is None:
            self.scraped_at = datetime.now().isoformat()


class BaseScraper(ABC):
    """Base class for all pricing scrapers"""
    
    def __init__(self, service_name: str, pricing_url: str):
        self.service_name = service_name
        self.pricing_url = pricing_url
    
    @abstractmethod
    async def scrape(self) -> List[PricingData]:
        """
        Scrape pricing data from the service
        Returns: List of PricingData objects
        """
        pass
    
    async def scrape_with_retry(self, max_retries: int = 3) -> List[PricingData]:
        """Scrape with exponential backoff retry logic"""
        for attempt in range(max_retries):
            try:
                return await self.scrape()
            except Exception as e:
                wait_time = 2 ** attempt
                logger.warning(f"Scrape attempt {attempt + 1} failed for {self.service_name}: {e}")
                if attempt < max_retries - 1:
                    logger.info(f"Retrying in {wait_time}s...")
                    await asyncio.sleep(wait_time)
                else:
                    logger.error(f"All retry attempts failed for {self.service_name}")
                    raise
        return []
