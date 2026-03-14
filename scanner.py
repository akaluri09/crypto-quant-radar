import ccxt
import math

print("\n🚀 Running Radar Scan...\n")

exchange = ccxt.coinbase({
    "enableRateLimit": True
})

tickers = exchange.fetch_tickers()

results = []

for symbol, data in tickers.items():

    if not symbol.endswith("/USD"):
        continue

    try:

        price = data["last"]
        change = data["percentage"]
        volume = data["baseVolume"]

        if price is None or change is None or volume is None:
            continue

        if volume < 500000:
            continue

        volume_score = math.log10(volume + 1)
        momentum_score = abs(change)

        score = volume_score + momentum_score

        if momentum_score > 5:
            results.append((symbol, score, price, change, volume))

    except:
        pass

results = sorted(results, key=lambda x: x[1], reverse=True)

print("🔥 RADAR SIGNALS\n")

for r in results[:15]:
    print(
        r[0],
        "| score:", round(r[1],2),
        "| price:", "{:.8f}".format(r[2]),
        "| change:", round(r[3],2),
        "| volume:", int(r[4])
    )
