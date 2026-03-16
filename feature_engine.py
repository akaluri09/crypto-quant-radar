import json
import os
import numpy as np

CANDLE_DIR = "data/candles"
OUTPUT_FILE = "compression_signals.json"


def load_candles(symbol_file):
    path = os.path.join(CANDLE_DIR, symbol_file)
    with open(path) as f:
        return json.load(f)


def parse_filename(file):
    # example: coinbase_BTC_USD.json
    name = file.replace(".json", "")
    parts = name.split("_")

    if len(parts) < 3:
        return None, None

    exchange = parts[0]
    symbol = f"{parts[1]}/{parts[2]}"
    return exchange, symbol


def compute_atr(candles, period):
    highs = [c[2] for c in candles]
    lows = [c[3] for c in candles]
    closes = [c[4] for c in candles]

    trs = []

    for i in range(1, len(candles)):
        high = highs[i]
        low = lows[i]
        prev_close = closes[i - 1]

        tr = max(
            high - low,
            abs(high - prev_close),
            abs(low - prev_close)
        )

        trs.append(tr)

    if len(trs) < period:
        return None

    return np.mean(trs[-period:])


def compression_signal(candles):
    atr_short = compute_atr(candles, 6)
    atr_long = compute_atr(candles, 24)

    if not atr_short or not atr_long or atr_long == 0:
        return None

    return atr_short / atr_long


def analyze_market():
    signals = []

    if not os.path.exists(CANDLE_DIR):
        return signals

    files = os.listdir(CANDLE_DIR)

    for file in files:
        if not file.endswith(".json"):
            continue

        try:
            exchange, symbol = parse_filename(file)
            if not exchange or not symbol:
                continue

            candles = load_candles(file)
            ratio = compression_signal(candles)

            if ratio is not None and ratio < 0.55:
                signals.append({
                    "exchange": exchange,
                    "symbol": symbol,
                    "compression_ratio": round(ratio, 3)
                })

        except Exception:
            continue

    signals = sorted(signals, key=lambda x: x["compression_ratio"])

    return signals[:30]


if __name__ == "__main__":
    signals = analyze_market()

    with open(OUTPUT_FILE, "w") as f:
        json.dump(signals, f, indent=2)

    print("\n⚡ Volatility Compression Signals\n")

    for s in signals:
        print(
            f"{s['exchange'].upper()} | {s['symbol']} | compression: {s['compression_ratio']}"
        )