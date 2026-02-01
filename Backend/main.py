from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests

app = FastAPI(title="Real-Time Crypto Tracker API")

# CORS (allow frontend later)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

COINGECKO_URL = "https://api.coingecko.com/api/v3/coins/markets"

@app.get("/")
def health_check():
    return {
        "status": "ok",
        "message": "Crypto Tracker Backend is running"
    }

@app.get("/prices")
def get_prices(
    limit: int = Query(10, ge=1, le=50),
    currency: str = Query("usd", pattern="^(usd|inr)$")
):
    try:
        params = {
            "vs_currency": currency,
            "order": "market_cap_desc",
            "per_page": limit,
            "page": 1,
            "sparkline": False
        }

        response = requests.get(COINGECKO_URL, params=params, timeout=10)

        if response.status_code != 200:
            raise HTTPException(
                status_code=502,
                detail="Failed to fetch data from CoinGecko"
            )

        data = response.json()

        # Return only clean fields
        clean_data = [
            {
                "name": coin["name"],
                "symbol": coin["symbol"],
                "price": coin["current_price"],
                "change_24h": coin["price_change_percentage_24h"],
                "market_cap": coin["market_cap"]
            }
            for coin in data
        ]

        return {
            "currency": currency,
            "count": len(clean_data),
            "data": clean_data
        }

    except requests.exceptions.RequestException:
        raise HTTPException(
            status_code=500,
            detail="External API error"
        )
