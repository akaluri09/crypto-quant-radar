import ccxt
import json
import os

print("🛸 Launching Quant Radar...")

exchange = ccxt.coinbase()
markets = exchange.load_markets()
symbols = list(markets.keys())
tickers = exchange.fetch_tickers()

DATA_DIR = "data/candles"
OUTPUT_FILE = "market_radar.json"

print(f"Scanning {len(symbols)} markets")

candidates = []
seen_assets = set()

CORE_ASSETS = {
    "BTC", "ETH", "SOL", "XRP", "ADA", "LINK", "AVAX",
    "HBAR", "UNI", "CRV", "DOGE", "LTC", "BCH", "AAVE", "FIL", "NEAR"
}

SPECULATIVE_ASSETS = {
    "PEPE", "SHIB", "FLOKI", "BONK", "TRUMP", "FARTCOIN",
    "USELESS", "WIF", "MOG", "POPCAT", "TURBO", "PENGU"
}

HAZARD_ASSETS = {
    "UP", "DOWN", "XAN", "A8", "OPN"
}


def load_candles(symbol):
    filename = symbol.replace("/", "_") + ".json"
    path = os.path.join(DATA_DIR, filename)

    if not os.path.exists(path):
        return []

    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception:
        return []


def compression_score(candles, lookback=24):
    if len(candles) < lookback:
        return 0

    recent = candles[-lookback:]
    ranges = []

    for candle in recent:
        high = candle[2]
        low = candle[3]
        close = candle[4]

        if close and close > 0:
            ranges.append((high - low) / close * 100)

    if not ranges:
        return 0

    avg_range = sum(ranges) / len(ranges)

    if avg_range < 0.4:
        return 30
    elif avg_range < 0.7:
        return 20
    elif avg_range < 1.0:
        return 10
    return 0


for symbol in symbols:

    if symbol not in tickers:
        continue

    asset = symbol.split("/")[0]

    # remove duplicate base assets
    if asset in seen_assets:
        continue
    seen_assets.add(asset)

    data = tickers[symbol]

    try:
        price = data["last"]
        volume = data["quoteVolume"]
        change = data["percentage"]

        if price is None or volume is None or change is None:
            continue

        # minimum liquidity
        if volume < 1_000_000:
            continue

        # current moonshot bias: favor lower-priced names
        if price > 10:
            continue

        # skip some mega caps to avoid overly mature names in this radar
        if asset in ["BTC", "ETH", "SOL", "BNB"]:
            continue

        # avoid chasing extreme pumps
        if change > 35:
            continue

        # ignore dead names
        if change < 1:
            continue

        candles = load_candles(symbol)
        comp_bonus = compression_score(candles)

        momentum_score = change * 8
        volume_score = min(volume / 1_000_000, 50)

        score = momentum_score + volume_score + comp_bonus

        # dashboard-friendly derived fields
        change_24h = round(change, 2)
        volume_heat = round(min(volume / 2_000_000, 5), 2)
        short_momentum = round(change / 3, 2)

        # make moonshot thesis explicit
        moonshot_bias = "ON"
        if asset in CORE_ASSETS or asset in ["XRP", "ADA", "LINK", "DOGE"]:
            moonshot_bias = "OFF"

        # classify quality tier
        if asset in CORE_ASSETS:
            quality_tier = "CORE"
        elif asset in SPECULATIVE_ASSETS:
            quality_tier = "SPECULATIVE"
        elif asset in HAZARD_ASSETS:
            quality_tier = "HAZARD"
        else:
            quality_tier = "MIDCAP"

        # human-readable setup explanation
        if comp_bonus >= 20 and change >= 2:
            setup_note = "Tight structure with breakout potential"
        elif change >= 10 and comp_bonus == 0:
            setup_note = "Momentum-led move, risk of chasing"
        elif comp_bonus >= 20:
            setup_note = "Compressed setup, waiting for expansion"
        else:
            setup_note = "Developing setup with moderate confirmation"

        candidates.append({
            "symbol": symbol,
            "price": price,
            "volume": volume,
            "change": change,
            "change_24h": change_24h,
            "volume_heat": volume_heat,
            "short_momentum": short_momentum,
            "compression_bonus": comp_bonus,
            "moonshot_bias": moonshot_bias,
            "quality_tier": quality_tier,
            "setup_note": setup_note,
            "score": round(score, 2)
        })

    except Exception:
        continue

candidates = sorted(candidates, key=lambda x: x["score"], reverse=True)

with open(OUTPUT_FILE, "w") as f:
    json.dump(candidates[:100], f, indent=2)

print("\n🚀 TOP QUANT RADAR SIGNALS\n")

for coin in candidates[:15]:
    print(
        f"{coin['symbol']} | score: {coin['score']} | "
        f"price: {coin['price']:.8f} | "
        f"24h change: {coin['change_24h']:.2f}% | "
        f"volume: {int(coin['volume'])} | "
        f"heat: {coin['volume_heat']:.2f}x | "
        f"compression bonus: {coin['compression_bonus']} | "
        f"tier: {coin['quality_tier']} | "
        f"moonshot: {coin['moonshot_bias']}"
    )

print(f"\nSaved ranked radar to {OUTPUT_FILE}")