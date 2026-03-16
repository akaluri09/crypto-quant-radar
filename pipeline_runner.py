import subprocess
import json
import os
import sys
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
        except Exception:
            return default
    return default


def save_json_file(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)


def main():
    started_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print("🚀 Starting Quant Pipeline")
    print("Time:", started_at)

    # --------------------------------
    # 1. Collect fresh market data
    # --------------------------------
    print("📡 Collecting market candles...")
    collector_output = run_command([sys.executable, "multi_exchange_collector.py"])

    # --------------------------------
    # 2. Market scan
    # --------------------------------
    print("🔎 Running market scanner...")
    scanner_output = run_command([sys.executable, "scanner.py"])

    # --------------------------------
    # 3. Volume anomaly detection
    # --------------------------------
    print("🔥 Running volume radar...")
    volume_output = run_command([sys.executable, "volume_radar.py"])

    # --------------------------------
    # 4. Discovery engine
    # --------------------------------
    print("🧠 Running discovery engine...")
    discovery_output = run_command([sys.executable, "discovery_engine.py"])

    # --------------------------------
    # 5. Signal generation
    # --------------------------------
    print("📊 Generating signals...")
    signal_output = run_command([sys.executable, "signal_engine.py"])

    # --------------------------------
    # 6. Alpha scoring
    # --------------------------------
    print("🧬 Running alpha engine...")
    alpha_output = run_command([sys.executable, "alpha_engine.py"])

    # --------------------------------
    # 7. Paper trading simulation
    # --------------------------------
    print("📈 Running paper trader...")
    trader_output = run_command([sys.executable, "paper_trader.py"])

    # --------------------------------
    # 8. Model statistics
    # --------------------------------
    print("📊 Updating model stats...")
    stats_output = run_command([sys.executable, "model_stats.py"])

    # --------------------------------
    # 9. Agent assistant summary
    # --------------------------------
    print("🤖 Generating agent brief...")
    agent_output = run_command([sys.executable, "agent.py"])

    # --------------------------------
    # Load latest data
    # --------------------------------
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
        "stats_output": stats_output,
        "collector_output": collector_output,
        "scanner_output": scanner_output,
        "discovery_output": discovery_output,
        "signal_output": signal_output,
        "trader_output": trader_output,
    }

    # --------------------------------
    # Save snapshot
    # --------------------------------
    save_json_file(SNAPSHOT_FILE, snapshot)

    # --------------------------------
    # Update run history
    # --------------------------------
    history = load_json_file(RUN_LOG_FILE, [])
    history.append(snapshot)
    history = history[-50:]
    save_json_file(RUN_LOG_FILE, history)

    # --------------------------------
    # Final output
    # --------------------------------
    print("\n🛸 Pipeline completed")
    print("Last run:", started_at)
    print("Signals:", snapshot["signal_count"])
    print("Open trades:", snapshot["open_trade_count"])
    print("Top signal:", snapshot["top_signal"])


if __name__ == "__main__":
    main()