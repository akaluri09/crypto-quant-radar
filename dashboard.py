import streamlit as st
import subprocess
import json
import os
import re

st.set_page_config(page_title="UFO Crypto Radar", layout="wide")

# ---------- style ----------
st.markdown("""
<style>
    .main {
        background-color: #0e1117;
    }
    .hero {
        padding: 1.25rem 1.5rem;
        border-radius: 18px;
        background: linear-gradient(135deg, #111827 0%, #0f172a 100%);
        border: 1px solid #1f2937;
        margin-bottom: 1rem;
    }
    .card {
        padding: 1rem 1.2rem;
        border-radius: 16px;
        background: #111827;
        border: 1px solid #1f2937;
        margin-bottom: 0.8rem;
    }
    .big {
        font-size: 1.8rem;
        font-weight: 700;
    }
    .muted {
        color: #9ca3af;
        font-size: 0.9rem;
    }
    .pill-green {
        display: inline-block;
        padding: 0.25rem 0.7rem;
        border-radius: 999px;
        background: rgba(34,197,94,0.15);
        color: #4ade80;
        font-weight: 700;
        font-size: 0.85rem;
    }
    .pill-yellow {
        display: inline-block;
        padding: 0.25rem 0.7rem;
        border-radius: 999px;
        background: rgba(250,204,21,0.15);
        color: #facc15;
        font-weight: 700;
        font-size: 0.85rem;
    }
    .pill-red {
        display: inline-block;
        padding: 0.25rem 0.7rem;
        border-radius: 999px;
        background: rgba(248,113,113,0.15);
        color: #f87171;
        font-weight: 700;
        font-size: 0.85rem;
    }
    .metric-box {
        padding: 0.9rem 1rem;
        border-radius: 14px;
        background: #0b1220;
        border: 1px solid #1f2937;
        text-align: center;
    }
    .metric-title {
        color: #9ca3af;
        font-size: 0.85rem;
    }
    .metric-value {
        font-size: 1.2rem;
        font-weight: 700;
        margin-top: 0.2rem;
    }
</style>
""", unsafe_allow_html=True)

# ---------- helpers ----------
def run_command(command):
    try:
        output = subprocess.check_output(command, text=True)
        return output
    except subprocess.CalledProcessError as e:
        return e.output
    except Exception as e:
        return str(e)

def load_json_file(filename, default):
    if os.path.exists(filename):
        try:
            with open(filename, "r") as f:
                return json.load(f)
        except:
            return default
    return default

def parse_alpha_output(output: str):
    rows = []
    for line in output.split("\n"):
        if "/USD" in line and "|" in line:
            parts = [p.strip() for p in line.split("|")]
            if len(parts) >= 3:
                symbol = parts[0]
                signal_type = parts[1]
                score_match = re.search(r"score:\s*([0-9.]+)", parts[2])
                score = float(score_match.group(1)) if score_match else 0.0
                rows.append({
                    "symbol": symbol,
                    "type": signal_type,
                    "score": score
                })
    return rows

def parse_volume_output(output: str):
    rows = {}
    for line in output.split("\n"):
        if "/USD" in line and "spike:" in line:
            match = re.search(r"^(.*?)\s*\|\s*spike:\s*([0-9.]+)x", line.strip())
            if match:
                symbol = match.group(1).strip()
                spike = float(match.group(2))
                rows[symbol] = spike
    return rows

def parse_stats_output(output: str):
    wins = losses = total = 0
    winrate = 0.0
    match = re.search(
        r"\{'wins':\s*(\d+),\s*'losses':\s*(\d+),\s*'total':\s*(\d+),\s*'winrate':\s*([0-9.]+)\}",
        output
    )
    if match:
        wins = int(match.group(1))
        losses = int(match.group(2))
        total = int(match.group(3))
        winrate = float(match.group(4))
    return {
        "wins": wins,
        "losses": losses,
        "total": total,
        "winrate": winrate
    }

def recommendation(score, spike):
    if score >= 250 or spike >= 1.8:
        return "PULL", "pill-green"
    if score >= 100 or spike >= 1.2:
        return "WATCH", "pill-yellow"
    return "AVOID", "pill-red"

def confidence(score, spike, model_winrate):
    # heuristic only
    raw = (score * 0.15) + (spike * 20) + (model_winrate * 0.35)
    return max(1, min(99, round(raw)))

def position_hint(price, bankroll=100):
    if not price or price <= 0:
        return "-"
    qty = bankroll / price
    return f"${bankroll} ≈ {qty:,.2f} tokens"

# ---------- top bar ----------
left, right = st.columns([4, 1])
with left:
    st.markdown('<div class="big">🛸 UFO Crypto Radar</div>', unsafe_allow_html=True)
    st.markdown('<div class="muted">Robinhood-style decision board for momentum, volume heat, paper trades, and model hit rate.</div>', unsafe_allow_html=True)
with right:
    if st.button("Refresh Radar"):
        run_command(["python", "scanner.py"])
        run_command(["python", "signal_engine.py"])
        st.rerun()

# ---------- load backend ----------
alpha_output = run_command(["python", "alpha_engine.py"])
volume_output = run_command(["python", "volume_radar.py"])
stats_output = run_command(["python", "model_stats.py"])

signals = load_json_file("signals.json", [])
trade_log = load_json_file("trade_log.json", [])

alpha_rows = parse_alpha_output(alpha_output)
volume_map = parse_volume_output(volume_output)
stats = parse_stats_output(stats_output)

for row in alpha_rows:
    row["spike"] = volume_map.get(row["symbol"], 0.0)
    row["call"], row["call_class"] = recommendation(row["score"], row["spike"])
    row["confidence"] = confidence(row["score"], row["spike"], stats["winrate"])

top_pick = alpha_rows[0] if alpha_rows else None

# ---------- hero card ----------
if top_pick:
    st.markdown('<div class="hero">', unsafe_allow_html=True)
    st.markdown(f"### 🏆 Best Setup Right Now: **{top_pick['symbol']}**")
    st.markdown(
        f"<span class='{top_pick['call_class']}'>{top_pick['call']}</span>",
        unsafe_allow_html=True
    )

    signal_details = next((s for s in signals if s.get("symbol") == top_pick["symbol"]), {})
    price = signal_details.get("price", 0)
    change = signal_details.get("change", 0)
    volume = signal_details.get("volume", 0)

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.markdown(
            f"<div class='metric-box'><div class='metric-title'>Price</div><div class='metric-value'>${price:.6f}</div></div>",
            unsafe_allow_html=True
        )
    with c2:
        st.markdown(
            f"<div class='metric-box'><div class='metric-title'>24h Move</div><div class='metric-value'>{change:.2f}%</div></div>",
            unsafe_allow_html=True
        )
    with c3:
        st.markdown(
            f"<div class='metric-box'><div class='metric-title'>Volume Heat</div><div class='metric-value'>{top_pick['spike']:.2f}x</div></div>",
            unsafe_allow_html=True
        )
    with c4:
        st.markdown(
            f"<div class='metric-box'><div class='metric-title'>Confidence</div><div class='metric-value'>{top_pick['confidence']}%</div></div>",
            unsafe_allow_html=True
        )
    with c5:
        st.markdown(
            f"<div class='metric-box'><div class='metric-title'>Starter Position</div><div class='metric-value'>{position_hint(price, 100)}</div></div>",
            unsafe_allow_html=True
        )

    st.markdown("</div>", unsafe_allow_html=True)

# ---------- tabs ----------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Top Setups", "Volume Heat", "Paper Trades", "Model Stats", "Deep Analysis"
])

with tab1:
    st.subheader("Top Setups Today")
    if not alpha_rows:
        st.write("No setups available yet. Refresh the radar.")
    else:
        for row in alpha_rows[:10]:
            signal_details = next((s for s in signals if s.get("symbol") == row["symbol"]), {})
            price = signal_details.get("price", 0)
            change = signal_details.get("change", 0)

            st.markdown('<div class="card">', unsafe_allow_html=True)
            c1, c2, c3 = st.columns([4, 2, 1])

            with c1:
                st.markdown(f"**{row['symbol']}**")
                st.markdown(
                    f"<span class='{row['call_class']}'>{row['call']}</span> &nbsp; "
                    f"<span class='muted'>confidence {row['confidence']}%</span>",
                    unsafe_allow_html=True
                )
                st.markdown(
                    f"<div class='muted'>Price ${price:.6f} · 24h {change:.2f}% · Volume heat {row['spike']:.2f}x</div>",
                    unsafe_allow_html=True
                )

            with c2:
                st.write(f"**Score:** {row['score']:.2f}")
                st.write(f"**Starter size:** {position_hint(price, 100)}")

            with c3:
                if st.button("Analyze", key=f"setup_{row['symbol']}"):
                    st.session_state["selected_symbol"] = row["symbol"]

            st.markdown('</div>', unsafe_allow_html=True)

with tab2:
    st.subheader("Volume Heat")
    if volume_map:
        sorted_volume = sorted(volume_map.items(), key=lambda x: x[1], reverse=True)
        for symbol, spike in sorted_volume[:10]:
            label, cls = recommendation(0, spike)
            st.markdown(
                f"<div class='card'><b>{symbol}</b> &nbsp; <span class='{cls}'>{label}</span>"
                f"<div class='muted'>Current volume running at <b>{spike:.2f}x</b> recent average.</div></div>",
                unsafe_allow_html=True
            )
    else:
        st.write("No strong volume heat at the moment.")

with tab3:
    st.subheader("Paper Trades")
    c1, c2 = st.columns([1, 3])
    with c1:
        if st.button("Run Paper Trader"):
            out = run_command(["python", "paper_trader.py"])
            st.text(out)
            st.rerun()

    open_trades = [t for t in trade_log if t.get("status") == "OPEN"]
    closed_trades = [t for t in trade_log if t.get("status") != "OPEN"]

    st.markdown("#### Open Trades")
    if open_trades:
        for trade in open_trades[-10:]:
            st.markdown(
                f"<div class='card'><b>{trade.get('symbol')}</b>"
                f"<div class='muted'>Entry: {trade.get('entry_price')} · Size: ${trade.get('size')} · Status: {trade.get('status')}</div></div>",
                unsafe_allow_html=True
            )
    else:
        st.write("No open trades.")

    st.markdown("#### Closed Trades")
    if closed_trades:
        for trade in closed_trades[-10:]:
            status = trade.get("status", "N/A")
            cls = "pill-green" if status == "WIN" else "pill-red"
            st.markdown(
                f"<div class='card'><b>{trade.get('symbol')}</b> "
                f"<span class='{cls}'>{status}</span>"
                f"<div class='muted'>Entry: {trade.get('entry_price')} · Exit: {trade.get('exit_price', '-')}</div></div>",
                unsafe_allow_html=True
            )
    else:
        st.write("No closed trades yet.")

with tab4:
    st.subheader("Model Stats")
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(
        f"<div class='metric-box'><div class='metric-title'>Trades</div><div class='metric-value'>{stats['total']}</div></div>",
        unsafe_allow_html=True
    )
    c2.markdown(
        f"<div class='metric-box'><div class='metric-title'>Wins</div><div class='metric-value'>{stats['wins']}</div></div>",
        unsafe_allow_html=True
    )
    c3.markdown(
        f"<div class='metric-box'><div class='metric-title'>Losses</div><div class='metric-value'>{stats['losses']}</div></div>",
        unsafe_allow_html=True
    )
    c4.markdown(
        f"<div class='metric-box'><div class='metric-title'>Win Rate</div><div class='metric-value'>{stats['winrate']:.2f}%</div></div>",
        unsafe_allow_html=True
    )
    st.markdown("#### Raw model output")
    st.text(stats_output)

with tab5:
    st.subheader("Deep Analysis")
    selected = st.session_state.get("selected_symbol", None)

    manual_symbol = st.text_input("Enter symbol manually", value=selected if selected else "")

    if st.button("Run Deep Scan"):
        if manual_symbol:
            deep_output = run_command(["python", "deep_scan.py", manual_symbol])
            st.text(deep_output)
        else:
            st.warning("Enter a symbol like APR/USD")
