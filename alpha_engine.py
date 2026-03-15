import json

SIGNALS_FILE = "signals.json"

print("🛸 Unified Alpha Engine")

try:
    with open(SIGNALS_FILE, "r") as f:
        signals = json.load(f)
except:
    signals = []

results = []

for coin in signals:

    symbol = coin["symbol"]
    signal_type = coin.get("type", "UNKNOWN")

    change = abs(float(coin.get("change", 0)))
    volume = float(coin.get("volume", 0))
    price = float(coin.get("price", 1))
    base_score = float(coin.get("score", 0))

    liquidity_score = volume / 1_000_000
    price_score = (1 / price) if price > 0 and price < 1 else 1
    listing_bonus = 25 if signal_type == "NEW_LISTING" else 0

    total_score = (
        base_score * 0.5 +
        change * 0.2 +
        liquidity_score * 0.2 +
        price_score * 0.1 +
        listing_bonus
    )

    results.append({
        "symbol": symbol,
        "type": signal_type,
        "score": total_score
    })

results = sorted(results, key=lambda x: x["score"], reverse=True)

print("\n🔥 TOP OPPORTUNITIES\n")

for coin in results[:10]:
    print(f"{coin['symbol']} | {coin['type']} | score: {round(coin['score'],2)}")
