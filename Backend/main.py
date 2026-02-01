from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import requests
import time

app = FastAPI()

# ------------------ CORS ------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # OK for demo/portfolio
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------ HEALTH CHECK ------------------
@app.get("/healthz")
def health_check():
    return {"status": "ok", "message": "Backend running"}

# ------------------ CACHE ------------------
CACHE = {}
CACHE_TTL = 60  # seconds

# ------------------ PRICES API ------------------
@app.get("/prices")
def get_prices(
    currency: str = Query("usd"),
    limit: int = Query(10, ge=1, le=50),
):
    cache_key = f"{currency}_{limit}"
    now = time.time()

    # Return cached data if valid
    if cache_key in CACHE:
        cached = CACHE[cache_key]
        if now - cached["timestamp"] < CACHE_TTL:
            return cached["data"]

    try:
        url = "https://api.coingecko.com/api/v3/coins/markets"
        params = {
            "vs_currency": currency,
            "order": "market_cap_desc",
            "per_page": limit,
            "page": 1,
            "sparkline": False,
            "price_change_percentage": "24h",
        }

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        coins = response.json()

        data = {
            "currency": currency,
            "count": len(coins),
            "data": [
                {
                    "name": c["name"],
                    "symbol": c["symbol"],
                    "price": c["current_price"],
                    "change_24h": c.get("price_change_percentage_24h"),
                    "market_cap": c["market_cap"],
                }
                for c in coins
            ],
        }

        CACHE[cache_key] = {
            "timestamp": now,
            "data": data,
        }

        return data

    except Exception:
        return {
            "currency": currency,
            "count": 0,
            "data": [],
            "warning": "Temporary data provider issue",
        }
