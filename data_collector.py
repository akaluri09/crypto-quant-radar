import ccxt
import json
import os
from datetime import datetime

exchange = ccxt.coinbase()

DATA_DIR = "data/candles"

os.makedirs(DATA_DIR, exist_ok=True)

TIMEFRAME = "5m"
LIMIT = 120


def get_markets():

    markets = exchange.load_markets()

    pairs = [
        m for m in markets
        if "/USD" in m and markets[m]["active"]
    ]

    return pairs[:300]


def collect():

    markets = get_markets()

    print(f"Collecting candles for {len(markets)} markets")

    for symbol in markets:

        try:

            candles = exchange.fetch_ohlcv(symbol, timeframe=TIMEFRAME, limit=LIMIT)

            filename = symbol.replace("/", "_") + ".json"

            path = os.path.join(DATA_DIR, filename)

            with open(path, "w") as f:
                json.dump(candles, f)

        except Exception:
            continue


if __name__ == "__main__":
    collect()