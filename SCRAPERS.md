# Pricing Scrapers

Automated pricing data collection from AI service providers.

## Architecture

```
scrapers/
├── base.py              # BaseScraper abstract class + PricingData model
├── openai_scraper.py    # OpenAI API pricing
├── anthropic_scraper.py # Anthropic Claude pricing
└── __init__.py          # Package exports

run_scrapers.py          # Runner script (executes all scrapers)
```

## Features

- **Concurrent scraping** - All scrapers run in parallel
- **Exponential backoff retry** - Automatic retry with 2^n second delays
- **Structured data** - Consistent PricingData format across all services
- **Database persistence** - Auto-save to SQLite via existing PricingDB

## Usage

### Install Dependencies

```bash
pip install -r requirements.txt
playwright install chromium
```

### Run All Scrapers

```bash
python run_scrapers.py
```

Output:
```
2026-02-04 10:45:00 - INFO - Running 2 scrapers...
2026-02-04 10:45:03 - INFO - ✓ Saved OpenAI GPT-4 - API
2026-02-04 10:45:03 - INFO - ✓ Saved OpenAI GPT-3.5 Turbo - API
2026-02-04 10:45:04 - INFO - ✓ Saved Anthropic Claude 3.5 Sonnet - API
2026-02-04 10:45:04 - INFO - ✓ Saved Anthropic Claude 3 Opus - API
2026-02-04 10:45:04 - INFO - ✓ Saved Anthropic Claude 3 Haiku - API
2026-02-04 10:45:04 - INFO - ✅ Successfully scraped and saved 5 pricing tiers
```

### Add a New Scraper

```python
# scrapers/elevenlabs_scraper.py
from playwright.async_api import async_playwright
from typing import List
from .base import BaseScraper, PricingData

class ElevenLabsScraper(BaseScraper):
    def __init__(self):
        super().__init__(
            service_name="ElevenLabs",
            pricing_url="https://elevenlabs.io/pricing"
        )
    
    async def scrape(self) -> List[PricingData]:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            try:
                await page.goto(self.pricing_url, wait_until="networkidle")
                
                # Extract pricing (adjust selectors to actual page structure)
                pricing_data = []
                
                starter_tier = PricingData(
                    service_name="ElevenLabs",
                    tier_name="Starter",
                    price_monthly=5.0,
                    price_usage="~$0.20/1K characters",
                    limits="30,000 chars/month",
                    features="10 voices, 3 custom voices",
                    url=self.pricing_url
                )
                pricing_data.append(starter_tier)
                
                return pricing_data
                
            finally:
                await browser.close()
```

Then register in `scrapers/__init__.py` and `run_scrapers.py`.

## Scheduling

### Option 1: Cron (Recommended)

```bash
# Run daily at 3 AM
0 3 * * * cd /path/to/agent-pricing-intel && python run_scrapers.py >> logs/scraper.log 2>&1
```

### Option 2: GitHub Actions

```yaml
# .github/workflows/scrape.yml
name: Daily Pricing Scrape
on:
  schedule:
    - cron: '0 3 * * *'  # 3 AM daily
jobs:
  scrape:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: |
          pip install -r requirements.txt
          playwright install chromium
          python run_scrapers.py
```

### Option 3: OpenClaw Cron

```bash
# From OpenClaw chat
@Bob schedule a daily cron job to run pricing scrapers at 3 AM PST
```

## Error Handling

Scrapers use exponential backoff:
- Attempt 1: Immediate
- Attempt 2: Wait 2s
- Attempt 3: Wait 4s
- Attempt 4+: Fail

Individual scraper failures don't block others (concurrent + exception handling).

## Adding Real DOM Scraping

Current scrapers have **hardcoded pricing** for MVP. To scrape live:

```python
async def scrape(self) -> List[PricingData]:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        try:
            await page.goto(self.pricing_url, wait_until="networkidle")
            
            # Wait for pricing table
            await page.wait_for_selector('.pricing-table', timeout=10000)
            
            # Extract price elements
            prices = await page.query_selector_all('.price-box')
            
            pricing_data = []
            for price_element in prices:
                tier_name = await price_element.query_selector('.tier-name')
                tier_name_text = await tier_name.inner_text()
                
                price = await price_element.query_selector('.price-amount')
                price_text = await price.inner_text()
                
                # Parse and structure
                pricing_data.append(PricingData(
                    service_name=self.service_name,
                    tier_name=tier_name_text,
                    price_monthly=float(price_text.strip('$')),
                    # ... other fields
                ))
            
            return pricing_data
            
        finally:
            await browser.close()
```

## Next Steps

1. **Replace hardcoded pricing with real DOM scraping** (use Playwright selectors)
2. **Add more services** (Midjourney, Replicate, Together AI, etc.)
3. **Implement change detection** (alert when pricing changes)
4. **Add screenshots** (save page screenshots for audit trail)
5. **Proxy rotation** (avoid rate limits for high-volume scraping)

## Production Deployment

For production scraping at scale:
- Use [Bright Data](https://brightdata.com) or [ScrapingBee](https://scrapingbee.com) for proxy rotation
- Deploy on [Fly.io](https://fly.io) or [Railway](https://railway.app) with scheduled tasks
- Store screenshots in S3 for audit trail
- Monitor with [Sentry](https://sentry.io) for scraper failures
