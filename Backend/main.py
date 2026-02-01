import time

CACHE = {}
CACHE_TTL = 60  # seconds


from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import requests

app = FastAPI(title="Real-Time Crypto Tracker API")

# ---------- CORS ----------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- CONSTANTS ----------
COINGECKO_URL = "https://api.coingecko.com/api/v3/coins/markets"
HEADERS = {
    "User-Agent": "Real-Time-Crypto-Tracker/1.0"
}

# ---------- HEALTH ----------
@app.get("/")
def root():
    return {"status": "ok", "message": "Backend running"}

# ---------- PRICES ----------
@app.get("/prices")
def get_prices(
    limit: int = Query(10, ge=1, le=50),
    currency: str = Query("usd", pattern="^(usd|inr)$")
):
    cache_key = f"{currency}_{limit}"
    now = time.time()

    # ✅ Serve cached data if valid
    if cache_key in CACHE:
        cached = CACHE[cache_key]
        if now - cached["timestamp"] < CACHE_TTL:
            return cached["data"]

    params = {
        "vs_currency": currency,
        "order": "market_cap_desc",
        "per_page": limit,
        "page": 1,
        "sparkline": False
    }

    try:
        response = requests.get(
            COINGECKO_URL,
            params=params,
            headers=HEADERS,
            timeout=10
        )

        if response.status_code != 200:
            if cache_key in CACHE:
                return CACHE[cache_key]["data"]

            return {
                "currency": currency,
                "count": 0,
                "data": [],
                "warning": "Temporary data provider issue"
            }

        raw_data = response.json()

        clean_data = [
            {
                "name": coin.get("name"),
                "symbol": coin.get("symbol"),
                "price": coin.get("current_price"),
                "change_24h": coin.get("price_change_percentage_24h"),
                "market_cap": coin.get("market_cap")
            }
            for coin in raw_data
        ]

        result = {
            "currency": currency,
            "count": len(clean_data),
            "data": clean_data
        }

        # ✅ Cache per (currency, limit)
        CACHE[cache_key] = {
            "timestamp": now,
            "data": result
        }

        return result

    except requests.exceptions.RequestException:
        if cache_key in CACHE:
            return CACHE[cache_key]["data"]

        return {
            "currency": currency,
            "count": 0,
            "data": [],
            "warning": "External API error"
        }
