import ccxt
import json
import os

print("\n🔍 Checking for new listings...\n")

exchanges = {
    "coinbase": ccxt.coinbase(),
    "kraken": ccxt.kraken()
}

database_file = "known_markets.json"

# load known markets
if os.path.exists(database_file):
    with open(database_file, "r") as f:
        known_markets = json.load(f)
else:
    known_markets = {}

new_listings = []

for name, exchange in exchanges.items():

    print("Scanning", name)

    try:
        markets = exchange.load_markets()
        symbols = [s for s in markets if s.endswith("/USD")]

        if name not in known_markets:
            known_markets[name] = []

        for symbol in symbols:
            if symbol not in known_markets[name]:
                new_listings.append((name, symbol))
                known_markets[name].append(symbol)

    except Exception as e:
        print("Error with", name)


# save updated database
with open(database_file, "w") as f:
    json.dump(known_markets, f)


if new_listings:

    print("\n🚀 NEW LISTINGS DETECTED\n")

    for exchange, symbol in new_listings:
        print(exchange.upper(), "|", symbol)

else:
    print("No new listings found.")
