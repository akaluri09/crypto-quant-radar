import subprocess
import json
import os
import time
from datetime import datetime

SNAPSHOT_FILE = "latest_snapshot.json"
RUN_LOG_FILE = "run_history.json"


def run_command(command):
    try:
        output = subprocess.check_output(command, text=True)
        return output
    except subprocess.CalledProcessError as e:
        return e.output
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


def main():
    started_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    scanner_output = run_command(["python", "scanner.py"])
    signal_output = run_command(["python", "signal_engine.py"])
    volume_output = run_command(["python", "volume_radar.py"])
    trader_output = run_command(["python", "paper_trader.py"])
    stats_output = run_command(["python", "model_stats.py"])
    agent_output = run_command(["python", "agent.py"])
    alpha_output = run_command(["python", "alpha_engine.py"])

    signals = load_json_file("signals.json", [])
    trades = load_json_file("trade_log.json", [])

    snapshot = {
        "last_run": started_at,
        "signal_count": len(signals),
        "open_trade_count": len([t for t in trades if t.get("status") == "OPEN"]),
        "top_signal": signals[0]["symbol"] if signals else None,
        "agent_brief": agent_output,
        "alpha_output": alpha_output,
        "volume_output": volume_output,
        "stats_output": stats_output
    }

    save_json_file(SNAPSHOT_FILE, snapshot)

    history = load_json_file(RUN_LOG_FILE, [])
    history.append(snapshot)
    history = history[-50:]  # keep last 50 runs
    save_json_file(RUN_LOG_FILE, history)

    print("🛸 Pipeline completed")
    print(f"Last run: {started_at}")
    print(f"Signals: {snapshot['signal_count']}")
    print(f"Open trades: {snapshot['open_trade_count']}")
    print(f"Top signal: {snapshot['top_signal']}")


if __name__ == "__main__":
    main()
