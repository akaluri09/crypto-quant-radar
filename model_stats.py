import json

TRADES_FILE = "trade_log.json"


def load_trades():
    try:
        with open(TRADES_FILE, "r") as f:
            return json.load(f)
    except:
        return []


def compute_stats():

    trades = load_trades()

    wins = 0
    losses = 0

    for trade in trades:

        if trade["status"] == "WIN":
            wins += 1

        if trade["status"] == "LOSS":
            losses += 1

    total = wins + losses

    winrate = 0

    if total > 0:
        winrate = wins / total * 100

    return {

        "wins": wins,
        "losses": losses,
        "total": total,
        "winrate": winrate
    }


if __name__ == "__main__":

    stats = compute_stats()

    print("Model Performance")
    print(stats)
