import ccxt
import pandas as pd
import json

print("🚀 Volume Explosion Radar")

exchange = ccxt.coinbase()

SIGNALS_FILE = "signals.json"

try:
    with open(SIGNALS_FILE, "r") as f:
        signals = json.load(f)
except:
    signals = []

if len(signals) == 0:
    print("No signals found. Run scanner first.")
    exit()

symbols = [coin["symbol"] for coin in signals[:25]]

print("Scanning:", symbols)

results = []

for symbol in symbols:

    try:

        candles = exchange.fetch_ohlcv(symbol, timeframe="5m", limit=20)

        df = pd.DataFrame(
            candles,
            columns=["time","open","high","low","close","volume"]
        )

        current_volume = df["volume"].iloc[-1]
        avg_volume = df["volume"].mean()

        if avg_volume == 0:
            continue

        spike = current_volume / avg_volume

        results.append({
            "symbol": symbol,
            "volume_spike": spike
        })

    except:
        continue


results = sorted(
    results,
    key=lambda x: x["volume_spike"],
    reverse=True
)

print("\n🔥 Top Volume Activity\n")

for coin in results[:10]:

    print(
        f"{coin['symbol']} | spike: {round(coin['volume_spike'],2)}x"
    )
