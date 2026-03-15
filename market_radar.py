import ccxt
import pandas as pd
import json
import os
import time

OUTPUT_FILE = "market_radar.json"

print("🛸 Running Full Market Radar...")

exchange = ccxt.coinbase({
    "enableRateLimit": True
})

markets = exchange.load_markets()

# -------------------------
# filters
# -------------------------
def is_valid_market(symbol, market):
    if not market.get("active", False):
        return False

    if not (symbol.endswith("/USD") or symbol.endswith("/USDC")):
        return False

    base = symbol.split("/")[0]

    banned_keywords = ["UP", "DOWN", "BULL", "BEAR", "3L", "3S", "PERP", "INTX"]
    for word in banned_keywords:
        if word in base:
            return False

    return True


symbols = [
    s for s, m in markets.items()
    if is_valid_market(s, m)
]

print(f"Scanning {len(symbols)} filtered markets")

# -------------------------
# get tickers first
# -------------------------
tickers = exchange.fetch_tickers()

candidates = []

for symbol in symbols:
    if symbol not in tickers:
        continue

    t = tickers[symbol]

    try:
        price = t["last"]
        volume = t["quoteVolume"]
        change = t["percentage"]

        if price is None or volume is None or change is None:
            continue

        # liquidity floor
        if volume < 250_000:
            continue

        candidates.append({
            "symbol": symbol,
            "price": float(price),
            "volume": float(volume),
            "change": float(change)
        })

    except Exception:
        continue

print(f"Liquid candidates: {len(candidates)}")

# -------------------------
# deep scan top liquid names
# -------------------------
# sort by liquidity first so we don't waste calls on dead names
candidates = sorted(candidates, key=lambda x: x["volume"], reverse=True)[:120]

results = []

for coin in candidates:
    symbol = coin["symbol"]

    try:
        candles = exchange.fetch_ohlcv(symbol, timeframe="5m", limit=24)

        df = pd.DataFrame(
            candles,
            columns=["time", "open", "high", "low", "close", "volume"]
        )

        if len(df) < 10:
            continue

        current_price = df["close"].iloc[-1]
        prev_price = df["close"].iloc[-4]   # ~20 min ago
        avg_vol = df["volume"].iloc[:-1].mean()
        current_vol = df["volume"].iloc[-1]

        if prev_price == 0 or avg_vol == 0:
            continue

        short_momentum = ((current_price - prev_price) / prev_price) * 100
        volume_heat = current_vol / avg_vol
        volatility = ((df["high"] - df["low"]) / df["close"]).replace([float("inf")], 0).fillna(0).mean() * 100

        # cheaper coins get a small moonshot bonus, but not insane
        price_bonus = 0
        if current_price < 1:
            price_bonus = 5
        elif current_price < 5:
            price_bonus = 2

        # unified ranking
        score = (
            abs(short_momentum) * 18 +
            volume_heat * 25 +
            abs(coin["change"]) * 2 +
            volatility * 8 +
            price_bonus
        )

        results.append({
            "symbol": symbol,
            "price": round(float(coin["price"]), 8),
            "change_24h": round(float(coin["change"]), 2),
            "volume": int(coin["volume"]),
            "short_momentum": round(float(short_momentum), 2),
            "volume_heat": round(float(volume_heat), 2),
            "volatility": round(float(volatility), 2),
            "score": round(float(score), 2)
        })

    except Exception:
        continue

    time.sleep(exchange.rateLimit / 1000)

results = sorted(results, key=lambda x: x["score"], reverse=True)

with open(OUTPUT_FILE, "w") as f:
    json.dump(results, f, indent=2)

print("\n🔥 TOP FULL-MARKET SIGNALS\n")

for row in results[:15]:
    print(
        f"{row['symbol']} | score: {row['score']} | "
        f"24h: {row['change_24h']}% | "
        f"short: {row['short_momentum']}% | "
        f"heat: {row['volume_heat']}x | "
        f"price: {row['price']}"
    )
