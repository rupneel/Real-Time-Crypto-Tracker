from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import requests
import time

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

COINGECKO_URL = "https://api.coingecko.com/api/v3/coins/markets"
CACHE = {
    "timestamp": 0,
    "data": []
}
CACHE_TTL = 60  # seconds

@app.get("/")
def root():
    return {"status": "ok", "message": "Backend running"}

@app.get("/healthz")
def health():
    return {"status": "healthy"}

@app.get("/prices")
def get_prices(currency: str = "usd", limit: int = 10):

    # 🔒 FORCE LIMITS (NO TOP 30)
    if limit not in [10, 20]:
        limit = 10

    now = time.time()

    # ✅ Serve cached data if fresh
    if CACHE["data"] and now - CACHE["timestamp"] < CACHE_TTL:
        return {
            "currency": currency,
            "count": limit,
            "data": CACHE["data"][:limit],
            "cached": True
        }

    try:
        params = {
            "vs_currency": currency,
            "order": "market_cap_desc",
            "per_page": 20,
            "page": 1,
            "sparkline": False,
            "price_change_percentage": "24h"
        }

        res = requests.get(COINGECKO_URL, params=params, timeout=10)
        res.raise_for_status()

        coins = res.json()

        formatted = [
            {
                "name": c["name"],
                "symbol": c["symbol"],
                "price": c["current_price"],
                "change_24h": c["price_change_percentage_24h"],
                "market_cap": c["market_cap"]
            }
            for c in coins
        ]

        # 💾 Cache success
        CACHE["data"] = formatted
        CACHE["timestamp"] = now

        return {
            "currency": currency,
            "count": limit,
            "data": formatted[:limit],
            "cached": False
        }

    except Exception as e:
        # 🛟 Fallback to cached data
        if CACHE["data"]:
            return {
                "currency": currency,
                "count": limit,
                "data": CACHE["data"][:limit],
                "cached": True,
                "warning": "Served from cache"
            }

        return {
            "currency": currency,
            "count": 0,
            "data": [],
            "error": "CoinGecko unavailable"
        }
