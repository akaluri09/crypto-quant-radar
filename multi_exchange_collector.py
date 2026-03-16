import ccxt
import json
import os
import time

DATA_DIR = "data/candles"
TIMEFRAME = "5m"
LIMIT = 120

EXCHANGES = [
    "coinbase",
    "kraken",
    "binance"
]

os.makedirs(DATA_DIR, exist_ok=True)


def get_exchange(name):
    exchange_class = getattr(ccxt, name)
    return exchange_class({
        "enableRateLimit": True
    })


def fetch_markets(exchange):

    markets = exchange.load_markets()

    pairs = []

    for symbol in markets:

        if "/USDT" in symbol or "/USD" in symbol or "/USDC" in symbol:

            if markets[symbol]["active"]:
                pairs.append(symbol)

    return pairs[:200]


def save_candles(symbol, candles):

    safe_symbol = symbol.replace("/", "_")

    path = os.path.join(DATA_DIR, f"{safe_symbol}.json")

    with open(path, "w") as f:
        json.dump(candles, f)


def collect_exchange(exchange_name):

    print(f"\nScanning {exchange_name}")

    exchange = get_exchange(exchange_name)

    pairs = fetch_markets(exchange)

    for symbol in pairs:

        try:

            candles = exchange.fetch_ohlcv(
                symbol,
                timeframe=TIMEFRAME,
                limit=LIMIT
            )

            save_candles(symbol, candles)

            time.sleep(exchange.rateLimit / 1000)

        except Exception:
            continue


def main():

    print("📡 Collecting multi-exchange market data")

    for name in EXCHANGES:

        try:
            collect_exchange(name)
        except Exception:
            continue

    print("\nMarket data collection complete")


if __name__ == "__main__":
    main()