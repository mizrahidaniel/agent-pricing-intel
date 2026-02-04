"""
Agent Pricing Intel - FastAPI Server
Serves pricing data via REST API
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import sqlite3
from scraper import PricingDB, PricingTier

app = FastAPI(title="Agent Pricing Intel API", version="0.1.0")

# CORS for web UI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PricingResponse(BaseModel):
    service_name: str
    tier_name: str
    price_monthly: Optional[float]
    price_usage: Optional[str]
    limits: str
    features: str
    url: str
    scraped_at: str

@app.get("/")
def root():
    return {
        "name": "Agent Pricing Intel API",
        "version": "0.1.0",
        "endpoints": {
            "/services": "List all tracked services",
            "/pricing/{service_name}": "Get pricing for a specific service",
            "/search?q=query": "Search pricing data"
        }
    }

@app.get("/services")
def list_services():
    """List all tracked services"""
    db = PricingDB()
    cursor = db.conn.execute("""
        SELECT DISTINCT service_name, COUNT(*) as tier_count
        FROM pricing_tiers
        GROUP BY service_name
        ORDER BY service_name
    """)
    services = [{"name": row[0], "tier_count": row[1]} for row in cursor.fetchall()]
    return {"services": services, "total": len(services)}

@app.get("/pricing/{service_name}", response_model=List[PricingResponse])
def get_pricing(service_name: str):
    """Get latest pricing for a service"""
    db = PricingDB()
    tiers = db.get_latest_pricing(service_name)
    if not tiers:
        raise HTTPException(status_code=404, detail=f"No pricing data for {service_name}")
    return [PricingResponse(**tier.__dict__) for tier in tiers]

@app.get("/search")
def search_pricing(q: str):
    """Search pricing data by service name or features"""
    db = PricingDB()
    cursor = db.conn.execute("""
        SELECT service_name, tier_name, price_monthly, price_usage, limits, features, url, scraped_at
        FROM pricing_tiers
        WHERE service_name LIKE ? OR features LIKE ?
        ORDER BY scraped_at DESC
        LIMIT 50
    """, (f"%{q}%", f"%{q}%"))
    
    results = []
    for row in cursor.fetchall():
        tier = PricingTier(*row)
        results.append(PricingResponse(**tier.__dict__))
    
    return {"results": results, "count": len(results)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
