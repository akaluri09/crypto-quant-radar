import subprocess
import json
import os
import sys
from datetime import datetime

RADAR_FILE = "market_radar.json"
SIGNALS_FILE = "signals.json"
TOP_N = 20


def load_json_file(filename, default):
    if os.path.exists(filename):
        try:
            with open(filename, "r") as f:
                return json.load(f)
        except Exception:
            return default
    return default


def save_json_file(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)


def run_command(command):
    try:
        return subprocess.check_output(command, text=True)
    except subprocess.CalledProcessError as e:
        return e.output
    except Exception as e:
        return f"ERROR: {e}"


print("\n🛸 UFO SIGNAL ENGINE ONLINE\n")

signals = []

# --------------------------------
# 1. Load ranked radar directly
# --------------------------------
radar = load_json_file(RADAR_FILE, [])

if not radar:
    print("No radar data found. Running scanner first...\n")
    scanner_output = run_command([sys.executable, "scanner.py"])
    print(scanner_output)
    radar = load_json_file(RADAR_FILE, [])

top_radar = radar[:TOP_N]

for coin in top_radar:
    try:
        symbol = coin["symbol"]
        score = float(coin.get("score", 0))
        price = float(coin.get("price", 0))
        change = float(coin.get("change", 0))
        volume = float(coin.get("volume", 0))
        compression_bonus = float(coin.get("compression_bonus", 0))

        signal_type = "BREAKOUT"

        if compression_bonus >= 20:
            signal_type = "COMPRESSED_BREAKOUT"

        signals.append({
            "type": signal_type,
            "symbol": symbol,
            "score": score,
            "price": price,
            "change": change,
            "volume": volume,
            "compression_bonus": compression_bonus,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

    except Exception:
        continue

# --------------------------------
# 2. Add listing detector signals
# --------------------------------
listing_output = run_command([sys.executable, "listing_detector.py"])
print(listing_output)

for line in listing_output.split("\n"):
    if "|" in line and ("COINBASE" in line or "KRAKEN" in line):
        try:
            parts = [p.strip() for p in line.split("|")]
            exchange = parts[0]
            symbol = parts[1]

            signals.append({
                "type": "NEW_LISTING",
                "symbol": symbol,
                "exchange": exchange,
                "score": 999,
                "price": 0,
                "change": 0,
                "volume": 0,
                "compression_bonus": 0,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })

        except Exception:
            continue

# --------------------------------
# 3. Sort highest score first
# --------------------------------
signals = sorted(signals, key=lambda x: x.get("score", 0), reverse=True)

# --------------------------------
# 4. Save signals
# --------------------------------
save_json_file(SIGNALS_FILE, signals)

print("\n👽 SIGNAL BOARD\n")

for s in signals[:25]:
    print(f"{s['type']} | {s['symbol']} | score={s['score']}")