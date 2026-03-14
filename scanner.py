import ccxt

print("🛸 Launching Moonshot Radar...")

exchange = ccxt.coinbase()

markets = exchange.load_markets()

symbols = list(markets.keys())

print(f"Scanning {len(symbols)} markets")

tickers = exchange.fetch_tickers()

candidates = []

seen_assets = set()

for symbol in symbols:

    if symbol not in tickers:
        continue

    asset = symbol.split("/")[0]

    # remove duplicate markets (USD / USDC / USDT)
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

        # Skip low liquidity
        if volume < 1_000_000:
            continue

        # Skip expensive assets (moonshot focus)
        if price > 10:
            continue

        # Skip mega caps
        if asset in ["BTC", "ETH", "SOL", "BNB"]:
            continue

        score = abs(change) * volume / 100000

        candidates.append({
            "symbol": symbol,
            "price": price,
            "volume": volume,
            "change": change,
            "score": score
        })

    except:
        continue

# Sort by momentum score
candidates = sorted(candidates, key=lambda x: x["score"], reverse=True)

print("\n🚀 TOP MOMENTUM SIGNALS\n")

for coin in candidates[:15]:

    print(
        f"{coin['symbol']} | score: {round(coin['score'],2)} | price: {coin['price']:.8f} | "
        f"24h change: {coin['change']}% | volume: {int(coin['volume'])}"
    )
