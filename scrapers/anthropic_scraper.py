"""
Anthropic pricing scraper
"""

from playwright.async_api import async_playwright
from typing import List
import logging
from .base import BaseScraper, PricingData

logger = logging.getLogger(__name__)


class AnthropicScraper(BaseScraper):
    """Scrape pricing from Anthropic's pricing page"""
    
    def __init__(self):
        super().__init__(
            service_name="Anthropic",
            pricing_url="https://www.anthropic.com/pricing"
        )
    
    async def scrape(self) -> List[PricingData]:
        """Extract pricing data from Anthropic"""
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            try:
                await page.goto(self.pricing_url, wait_until="networkidle")
                
                pricing_data = []
                
                # Claude 3.5 Sonnet
                sonnet_data = PricingData(
                    service_name="Anthropic Claude 3.5 Sonnet",
                    tier_name="API",
                    price_monthly=None,
                    price_usage="$0.003/1K tokens (input), $0.015/1K tokens (output)",
                    limits="Rate limits by tier",
                    features="200K context, vision, JSON mode, tool use",
                    url=self.pricing_url
                )
                pricing_data.append(sonnet_data)
                
                # Claude 3 Opus
                opus_data = PricingData(
                    service_name="Anthropic Claude 3 Opus",
                    tier_name="API",
                    price_monthly=None,
                    price_usage="$0.015/1K tokens (input), $0.075/1K tokens (output)",
                    limits="Rate limits by tier",
                    features="200K context, most capable, vision, tool use",
                    url=self.pricing_url
                )
                pricing_data.append(opus_data)
                
                # Claude 3 Haiku (fast + cheap)
                haiku_data = PricingData(
                    service_name="Anthropic Claude 3 Haiku",
                    tier_name="API",
                    price_monthly=None,
                    price_usage="$0.00025/1K tokens (input), $0.00125/1K tokens (output)",
                    limits="Rate limits by tier",
                    features="200K context, fastest, most affordable",
                    url=self.pricing_url
                )
                pricing_data.append(haiku_data)
                
                logger.info(f"Successfully scraped {len(pricing_data)} tiers from Anthropic")
                return pricing_data
                
            except Exception as e:
                logger.error(f"Error scraping Anthropic: {e}")
                raise
            finally:
                await browser.close()
