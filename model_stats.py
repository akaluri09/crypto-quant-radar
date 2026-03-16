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

    win_returns = []
    loss_returns = []

    for trade in trades:

        status = trade.get("status")
        pnl = trade.get("pnl_pct", 0)

        if status == "WIN":
            wins += 1
            win_returns.append(pnl)

        if status == "LOSS":
            losses += 1
            loss_returns.append(pnl)

    total = wins + losses

    winrate = (wins / total * 100) if total > 0 else 0

    avg_win = sum(win_returns) / len(win_returns) if win_returns else 0
    avg_loss = sum(loss_returns) / len(loss_returns) if loss_returns else 0

    gross_win = sum(win_returns)
    gross_loss = abs(sum(loss_returns))

    profit_factor = gross_win / gross_loss if gross_loss > 0 else 0

    expectancy = ((wins / total) * avg_win + (losses / total) * avg_loss) if total > 0 else 0

    return {
        "wins": wins,
        "losses": losses,
        "total": total,
        "winrate": winrate,
        "avg_win_pct": avg_win,
        "avg_loss_pct": avg_loss,
        "profit_factor": profit_factor,
        "expectancy_per_trade": expectancy
    }


if __name__ == "__main__":

    stats = compute_stats()

    print("\nModel Performance")
    print(json.dumps(stats, indent=2))