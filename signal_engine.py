import subprocess
import json

print("\n🛸 UFO SIGNAL ENGINE ONLINE\n")

signals = []

# run scanner
scanner_output = subprocess.check_output(
    ["python", "scanner.py"]
).decode()

print(scanner_output)

for line in scanner_output.split("\n"):

    if "/USD" in line and "|" in line:

        try:
            parts = [p.strip() for p in line.split("|")]

            symbol = parts[0]
            score = float(parts[1].split(":")[1].strip())
            price = float(parts[2].split(":")[1].strip())
            change_text = parts[3].split(":")[1].strip().replace("%", "")
            change = float(change_text)
            volume = float(parts[4].split(":")[1].strip())

            signals.append({
                "type": "BREAKOUT",
                "symbol": symbol,
                "score": score,
                "price": price,
                "change": change,
                "volume": volume
            })

        except:
            continue


# run listing detector
listing_output = subprocess.check_output(
    ["python", "listing_detector.py"]
).decode()

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
                "score": 999,   # huge bonus for new listings
                "price": 0,
                "change": 0,
                "volume": 0
            })

        except:
            continue


with open("signals.json", "w") as f:
    json.dump(signals, f, indent=2)

print("\n👽 SIGNAL BOARD\n")

for s in signals:
    print(f"{s['type']} | {s['symbol']} | score={s['score']}")
