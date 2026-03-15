import json
import ccxt
import time

exchange = ccxt.coinbase()

SIGNALS_FILE = "signals.json"
TRADES_FILE = "trade_log.json"

TRADE_SIZE = 100


def load_signals():
    try:
        with open(SIGNALS_FILE, "r") as f:
            return json.load(f)
    except:
        return []


def load_trades():
    try:
        with open(TRADES_FILE, "r") as f:
            return json.load(f)
    except:
        return []


def save_trades(trades):
    with open(TRADES_FILE, "w") as f:
        json.dump(trades, f, indent=4)


def get_price(symbol):
    try:
        ticker = exchange.fetch_ticker(symbol)
        return ticker["last"]
    except:
        return None


def open_trade(symbol, price):

    trades = load_trades()

    trade = {
        "symbol": symbol,
        "entry_price": price,
        "size": TRADE_SIZE,
        "status": "OPEN",
        "timestamp": time.time()
    }

    trades.append(trade)

    save_trades(trades)


def evaluate_trades():

    trades = load_trades()

    for trade in trades:

        if trade["status"] != "OPEN":
            continue

        symbol = trade["symbol"]
        entry = trade["entry_price"]

        try:

            current = get_price(symbol)

            if current is None:
                continue

            change = (current - entry) / entry * 100

            if change >= 5:
                trade["status"] = "WIN"
                trade["exit_price"] = current

            elif change <= -3:
                trade["status"] = "LOSS"
                trade["exit_price"] = current

        except:
            continue

    save_trades(trades)


def run():

    print("Running paper trader...")

    signals = load_signals()
    trades = load_trades()

    open_symbols = {t["symbol"] for t in trades if t["status"] == "OPEN"}

    for coin in signals[:5]:

        symbol = coin["symbol"]

        if symbol in open_symbols:
            continue

        price = get_price(symbol)

        if price is None:
            continue

        open_trade(symbol, price)

    evaluate_trades()


if __name__ == "__main__":
    run()
