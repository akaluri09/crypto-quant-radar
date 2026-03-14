import subprocess
import json

print("\n🛸 UFO SIGNAL ENGINE ONLINE\n")

signals = []

# run breakout radar
scanner_output = subprocess.check_output(
    ["python", "scanner.py"]
).decode()

for line in scanner_output.split("\n"):

    if "/USD" in line:

        symbol = line.split("|")[0].strip()

        signals.append({
            "type": "BREAKOUT",
            "symbol": symbol
        })


# run listing detector
listing_output = subprocess.check_output(
    ["python", "listing_detector.py"]
).decode()

for line in listing_output.split("\n"):

    if "|" in line:

        parts = line.split("|")

        exchange = parts[0].strip()
        symbol = parts[1].strip()

        signals.append({
            "type": "NEW_LISTING",
            "symbol": symbol,
            "exchange": exchange
        })


# save signals
with open("signals.json", "w") as f:
    json.dump(signals, f, indent=2)


print("\n👽 SIGNAL BOARD\n")

for s in signals:

    if s["type"] == "BREAKOUT":
        print("🛸 BREAKOUT:", s["symbol"])

    if s["type"] == "NEW_LISTING":
        print("👾 NEW LISTING:", s["symbol"], "on", s["exchange"])
