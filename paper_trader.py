import json
import ccxt
import time

exchange = ccxt.coinbase()

SIGNALS_FILE = "signals.json"
TRADES_FILE = "trade_log.json"

TRADE_SIZE = 100
MAX_NEW_TRADES_PER_RUN = 5
MIN_SCORE = 60

BLACKLIST = {
    "USELESS",
    "FARTCOIN",
    "TRUMP"
}


def load_signals():
    try:
        with open(SIGNALS_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return []


def load_trades():
    try:
        with open(TRADES_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return []


def save_trades(trades):
    with open(TRADES_FILE, "w") as f:
        json.dump(trades, f, indent=4)


def get_price(symbol):
    try:
        ticker = exchange.fetch_ticker(symbol)
        return ticker["last"]
    except Exception:
        return None


def symbol_base(symbol):
    return symbol.split("/")[0]


def is_quality_signal(signal):
    base = symbol_base(signal["symbol"])
    signal_type = signal.get("type", "")
    score = float(signal.get("score", 0))
    compression_bonus = float(signal.get("compression_bonus", 0))
    change = float(signal.get("change", 0))

    # 1. blacklist obvious junk
    if base in BLACKLIST:
        return False

    # 2. minimum score
    if score < MIN_SCORE:
        return False

    # 3. prefer compressed breakouts
    if signal_type == "COMPRESSED_BREAKOUT":
        return True

    # 4. plain breakouts need stricter quality
    if signal_type == "BREAKOUT":
        if compression_bonus > 0:
            return True
        if score >= 90 and change <= 15:
            return True

    return False


def open_trade(signal, price):
    trades = load_trades()

    trade = {
        "symbol": signal["symbol"],
        "entry_price": price,
        "size": TRADE_SIZE,
        "status": "OPEN",
        "signal_type": signal.get("type", "UNKNOWN"),
        "signal_score": signal.get("score", 0),
        "compression_bonus": signal.get("compression_bonus", 0),
        "signal_change": signal.get("change", 0),
        "opened_at": time.time()
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
                trade["pnl_pct"] = round(change, 4)
                trade["closed_at"] = time.time()

            elif change <= -3:
                trade["status"] = "LOSS"
                trade["exit_price"] = current
                trade["pnl_pct"] = round(change, 4)
                trade["closed_at"] = time.time()

        except Exception:
            continue

    save_trades(trades)


def run():
    print("Running paper trader...")

    signals = load_signals()
    trades = load_trades()

    open_symbols = {t["symbol"] for t in trades if t["status"] == "OPEN"}

    new_trades_opened = 0

    for signal in signals:
        if new_trades_opened >= MAX_NEW_TRADES_PER_RUN:
            break

        symbol = signal["symbol"]

        if symbol in open_symbols:
            continue

        if not is_quality_signal(signal):
            continue

        price = get_price(symbol)

        if price is None:
            continue

        open_trade(signal, price)
        new_trades_opened += 1

    evaluate_trades()


if __name__ == "__main__":
    run()