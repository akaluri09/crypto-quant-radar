import json
import os
from datetime import datetime

MARKET_FILE = "market_radar.json"
KNOWN_FILE = "known_discoveries.json"
OUTPUT_FILE = "discovery_radar.json"


def load_json(path, default):
    if os.path.exists(path):
        try:
            with open(path, "r") as f:
                return json.load(f)
        except:
            return default
    return default


def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


market = load_json(MARKET_FILE, [])
known = load_json(KNOWN_FILE, {})

now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

results = []
seen_assets = set()

for coin in market:
    symbol = coin["symbol"]
    base = symbol.split("/")[0]

    # remove duplicate USD / USDC versions
    if base in seen_assets:
        continue
    seen_assets.add(base)

    if symbol not in known:
        known[symbol] = {
            "first_seen": now,
            "times_seen": 1
        }
        freshness_bonus = 25
    else:
        known[symbol]["times_seen"] += 1
        freshness_bonus = max(0, 25 - (known[symbol]["times_seen"] * 2))

    score = float(coin.get("score", 0))
    heat = float(coin.get("volume_heat", 0))
    short_momentum = abs(float(coin.get("short_momentum", 0)))
    price = float(coin.get("price", 1))
    change_24h = abs(float(coin.get("change_24h", 0)))

    price_bonus = 0
    if 0 < price < 1:
        price_bonus = 8
    elif price < 5:
        price_bonus = 3

    discovery_score = (
        score * 0.45 +
        heat * 18 +
        short_momentum * 14 +
        change_24h * 2 +
        freshness_bonus +
        price_bonus
    )

    results.append({
        "symbol": symbol,
        "price": price,
        "score": round(score, 2),
        "volume_heat": round(heat, 2),
        "short_momentum": round(short_momentum, 2),
        "change_24h": round(change_24h, 2),
        "freshness_bonus": round(freshness_bonus, 2),
        "discovery_score": round(discovery_score, 2),
        "first_seen": known[symbol]["first_seen"],
        "times_seen": known[symbol]["times_seen"]
    })

results = sorted(results, key=lambda x: x["discovery_score"], reverse=True)

save_json(KNOWN_FILE, known)
save_json(OUTPUT_FILE, results)

print("\n🧠 Discovery Radar\n")
print("Top fresh asymmetric signals:\n")

for row in results[:15]:
    print(
        f"{row['symbol']} | discovery: {row['discovery_score']} | "
        f"heat: {row['volume_heat']}x | "
        f"short: {row['short_momentum']}% | "
        f"24h: {row['change_24h']}% | "
        f"freshness: {row['freshness_bonus']}"
    )
