import ccxt
import pandas as pd
import sys

print("\n🔎 Deep Scan Starting...\n")

exchange = ccxt.coinbase({
    "enableRateLimit": True
})

if len(sys.argv) < 2:
    print("Usage: python deep_scan.py SYMBOL")
    print("Example: python deep_scan.py PRCL/USD")
    exit()

symbol = sys.argv[1]

print("Analyzing:", symbol)

candles = exchange.fetch_ohlcv(symbol, timeframe="5m", limit=200)

df = pd.DataFrame(
    candles,
    columns=["time","open","high","low","close","volume"]
)

price = df["close"].iloc[-1]

avg_volume = df["volume"].mean()
latest_volume = df["volume"].iloc[-1]

if avg_volume == 0:
    rvol = 0
else:
    rvol = latest_volume / avg_volume

recent_high = df["high"].max()

volatility = (df["high"] - df["low"]).mean()

print("\n=========================")
print("Symbol:", symbol)
print("Current price:", price)
print("Relative volume:", round(rvol,2))
print("Recent high:", recent_high)
print("Volatility:", round(volatility,6))
print("=========================\n")

if price >= recent_high:
    print("🚀 BREAKOUT DETECTED\n")

if rvol > 3:
    print("🔥 HIGH RELATIVE VOLUME\n")
