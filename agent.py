import json
import os
import subprocess
import time
import ast

SIGNALS_FILE = "signals.json"
TRADE_LOG_FILE = "trade_log.json"
MEMORY_FILE = "assistant_memory.json"


def run_command(command):
    try:
        return subprocess.check_output(command, text=True)
    except Exception as e:
        return f"ERROR: {e}"


def load_json_file(filename, default):
    if os.path.exists(filename):
        try:
            with open(filename, "r") as f:
                return json.load(f)
        except:
            return default
    return default


def save_json_file(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)


def get_model_stats():
    output = run_command(["python", "model_stats.py"])
    stats = {"wins": 0, "losses": 0, "total": 0, "winrate": 0.0}

    try:
        lines = [line.strip() for line in output.split("\n") if line.strip()]
        parsed = ast.literal_eval(lines[-1])
        stats.update(parsed)
    except:
        pass

    return stats


def recommendation(score, price, change, volume):
    if score >= 250 and change >= 8 and volume >= 1_500_000:
        return "PULL"
    if score >= 100 and change >= 2:
        return "WATCH"
    return "AVOID"


def confidence(score, winrate, volume):
    value = 20
    value += min(score / 15, 40)
    value += min(winrate / 4, 20)
    value += min(volume / 2_000_000, 20)
    return round(max(1, min(value, 99)), 1)


def starter_size(price, bankroll=100):
    if not price or price <= 0:
        return "-"
    qty = bankroll / price
    return f"${bankroll} ≈ {qty:,.2f} tokens"


def build_brief():
    signals = load_json_file(SIGNALS_FILE, [])
    trades = load_json_file(TRADE_LOG_FILE, [])
    memory = load_json_file(MEMORY_FILE, {
        "last_top_symbol": None,
        "last_run": None
    })

    stats = get_model_stats()

    if not signals:
        return {
            "summary": "No signals available yet. Refresh the radar first.",
            "top_pick": None,
            "watchlist": [],
            "open_trades": [],
            "stats": stats,
            "changes": []
        }

    ranked = sorted(signals, key=lambda x: float(x.get("score", 0)), reverse=True)

    top = ranked[0]
    top_symbol = top.get("symbol")
    top_score = float(top.get("score", 0))
    top_price = float(top.get("price", 0))
    top_change = float(top.get("change", 0))
    top_volume = float(top.get("volume", 0))

    top_pick = {
        "symbol": top_symbol,
        "score": round(top_score, 2),
        "price": top_price,
        "change": round(top_change, 2),
        "volume": int(top_volume),
        "call": recommendation(top_score, top_price, top_change, top_volume),
        "confidence": confidence(top_score, stats["winrate"], top_volume),
        "starter_size": starter_size(top_price, 100)
    }

    watchlist = []
    for coin in ranked[1:6]:
        score = float(coin.get("score", 0))
        price = float(coin.get("price", 0))
        change = float(coin.get("change", 0))
        volume = float(coin.get("volume", 0))

        watchlist.append({
            "symbol": coin.get("symbol"),
            "score": round(score, 2),
            "change": round(change, 2),
            "call": recommendation(score, price, change, volume)
        })

    open_trades = [t for t in trades if t.get("status") == "OPEN"][-5:]

    changes = []

    if memory.get("last_top_symbol") != top_symbol:
        if memory.get("last_top_symbol"):
            changes.append(
                f"Top pick changed from {memory['last_top_symbol']} to {top_symbol}."
            )
        else:
            changes.append(f"Initial top pick is {top_symbol}.")

    changes.append(
        f"Model win rate currently sits at {round(stats['winrate'], 2)}%."
    )

    summary = (
        f"Top setup right now is {top_symbol}. "
        f"Call: {top_pick['call']}. "
        f"Confidence: {top_pick['confidence']}%. "
        f"Starter position: {top_pick['starter_size']}."
    )

    memory["last_top_symbol"] = top_symbol
    memory["last_run"] = time.time()
    save_json_file(MEMORY_FILE, memory)

    return {
        "summary": summary,
        "top_pick": top_pick,
        "watchlist": watchlist,
        "open_trades": open_trades,
        "stats": stats,
        "changes": changes
    }


def print_brief(brief):
    print("\n🛸 AGENT BRIEF\n")

    print("Summary:")
    print(brief["summary"])
    print()

    if brief["top_pick"]:
        top = brief["top_pick"]
        print("Top Pick:")
        print(f"  Symbol: {top['symbol']}")
        print(f"  Score: {top['score']}")
        print(f"  Price: ${top['price']}")
        print(f"  24h Move: {top['change']}%")
        print(f"  Call: {top['call']}")
        print(f"  Confidence: {top['confidence']}%")
        print(f"  Starter Size: {top['starter_size']}")
        print()

    print("Watchlist:")
    for coin in brief["watchlist"]:
        print(
            f"  {coin['symbol']} | score: {coin['score']} | "
            f"change: {coin['change']}% | {coin['call']}"
        )
    print()

    print("What changed:")
    for item in brief["changes"]:
        print(f"  - {item}")
    print()

    print("Open Trades:")
    if brief["open_trades"]:
        for trade in brief["open_trades"]:
            print(
                f"  {trade.get('symbol')} | entry: {trade.get('entry_price')} | "
                f"status: {trade.get('status')}"
            )
    else:
        print("  No open trades.")
    print()

    print("Model Stats:")
    print(
        f"  Trades: {brief['stats']['total']} | "
        f"Wins: {brief['stats']['wins']} | "
        f"Losses: {brief['stats']['losses']} | "
        f"Win Rate: {round(brief['stats']['winrate'], 2)}%"
    )


if __name__ == "__main__":
    brief = build_brief()
    print_brief(brief)
