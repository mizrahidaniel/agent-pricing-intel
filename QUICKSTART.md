# Quick Start

## Install & Run (30 seconds)

```bash
# Install dependencies
pip install -r requirements.txt

# Seed database with pricing data
python scraper.py

# Start API server
python api.py
```

API runs at http://localhost:8000

## API Examples

```bash
# List all services
curl http://localhost:8000/services

# Get OpenAI pricing
curl http://localhost:8000/pricing/OpenAI%20GPT-4

# Search for image generation services
curl http://localhost:8000/search?q=image
```

## Current Data (MVP)
- OpenAI GPT-4 API
- Anthropic Claude API  
- ElevenLabs (Starter, Creator tiers)
- Midjourney (Basic, Standard tiers)

More services coming soon!
