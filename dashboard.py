import streamlit as st
import subprocess
import json
import os
import re

st.set_page_config(page_title="UFO Crypto Radar", layout="wide")

# -------------------------
# STYLE
# -------------------------
st.markdown("""
<style>
    .main {
        background-color: #0b1220;
    }

    .hero {
        padding: 1.4rem 1.4rem 1.2rem 1.4rem;
        border-radius: 22px;
        background: linear-gradient(135deg, #111827 0%, #0f172a 100%);
        border: 1px solid #1f2937;
        margin-bottom: 1.2rem;
    }

    .section-card {
        padding: 1rem 1.1rem;
        border-radius: 18px;
        background: #111827;
        border: 1px solid #1f2937;
        margin-bottom: 0.9rem;
    }

    .mini-card {
        padding: 0.85rem 1rem;
        border-radius: 16px;
        background: #0f172a;
        border: 1px solid #1f2937;
        text-align: center;
    }

    .hero-title {
        font-size: 2rem;
        font-weight: 800;
        line-height: 1.1;
    }

    .hero-sub {
        color: #9ca3af;
        font-size: 0.95rem;
        margin-top: 0.3rem;
    }

    .symbol-big {
        font-size: 1.6rem;
        font-weight: 800;
    }

    .muted {
        color: #9ca3af;
        font-size: 0.9rem;
    }

    .metric-label {
        color: #9ca3af;
        font-size: 0.82rem;
        margin-bottom: 0.15rem;
    }

    .metric-value {
        font-size: 1.15rem;
        font-weight: 700;
    }

    .pill-green, .pill-yellow, .pill-red, .pill-blue {
        display: inline-block;
        padding: 0.28rem 0.75rem;
        border-radius: 999px;
        font-weight: 700;
        font-size: 0.8rem;
    }

    .pill-green {
        background: rgba(34,197,94,0.14);
        color: #4ade80;
    }

    .pill-yellow {
        background: rgba(250,204,21,0.14);
        color: #facc15;
    }

    .pill-red {
        background: rgba(248,113,113,0.14);
        color: #f87171;
    }

    .pill-blue {
        background: rgba(96,165,250,0.14);
        color: #60a5fa;
    }

    .divider-space {
        height: 0.4rem;
    }

    .top-setup-card {
        padding: 1rem 1.1rem;
        border-radius: 18px;
        background: #111827;
        border: 1px solid #1f2937;
        margin-bottom: 0.75rem;
    }

    .small-note {
        color: #94a3b8;
        font-size: 0.82rem;
    }
</style>
""", unsafe_allow_html=True)

# -------------------------
# HELPERS
# -------------------------
def run_command(command):
    try:
        return subprocess.check_output(command, text=True)
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

def parse_alpha_output(output):
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

def parse_volume_output(output):
    rows = []
    for line in output.split("\n"):
        if "/USD" in line and "spike:" in line:
            m = re.search(r"^(.*?)\s*\|\s*spike:\s*([0-9.]+)x", line.strip())
            if m:
                rows.append({
                    "symbol": m.group(1).strip(),
                    "spike": float(m.group(2))
                })
    return rows

def parse_stats_output(output):
    wins = losses = total = 0
    winrate = 0.0
    m = re.search(
        r"\{'wins':\s*(\d+),\s*'losses':\s*(\d+),\s*'total':\s*(\d+),\s*'winrate':\s*([0-9.]+)\}",
        output
    )
    if m:
        wins = int(m.group(1))
        losses = int(m.group(2))
        total = int(m.group(3))
        winrate = float(m.group(4))
    return {
        "wins": wins,
        "losses": losses,
        "total": total,
        "winrate": winrate
    }

def recommendation(score, change, spike):
    if score >= 250 and change >= 8:
        return ("PULL", "pill-green")
    if score >= 100 or spike >= 1.5:
        return ("WATCH", "pill-yellow")
    return ("AVOID", "pill-red")

def confidence(score, spike, winrate):
    raw = (score * 0.08) + (spike * 18) + (winrate * 0.35)
    return max(1, min(99, round(raw)))

def starter_size(price, bankroll=100):
    if not price or price <= 0:
        return "-"
    qty = bankroll / price
    return f"${bankroll} ≈ {qty:,.2f} tokens"

def short_reason(change, spike, score):
    reasons = []
    if change >= 10:
        reasons.append("strong momentum")
    elif change >= 3:
        reasons.append("decent momentum")
    else:
        reasons.append("weak momentum")

    if spike >= 1.8:
        reasons.append("volume heating up")
    elif spike >= 1.2:
        reasons.append("some volume support")
    else:
        reasons.append("volume not explosive")

    if score >= 250:
        reasons.append("high ranking signal")
    elif score >= 100:
        reasons.append("moderate ranking signal")
    else:
        reasons.append("lower ranking signal")

    return ", ".join(reasons)

# -------------------------
# LOAD BACKEND
# -------------------------
signals = load_json_file("signals.json", [])
trade_log = load_json_file("trade_log.json", [])

alpha_output = run_command(["python", "alpha_engine.py"])
volume_output = run_command(["python", "volume_radar.py"])
stats_output = run_command(["python", "model_stats.py"])
agent_output = run_command(["python", "agent.py"])

alpha_rows = parse_alpha_output(alpha_output)
volume_rows = parse_volume_output(volume_output)
stats = parse_stats_output(stats_output)

volume_map = {row["symbol"]: row["spike"] for row in volume_rows}

for row in alpha_rows:
    signal_data = next((s for s in signals if s.get("symbol") == row["symbol"]), {})
    row["price"] = float(signal_data.get("price", 0))
    row["change"] = float(signal_data.get("change", 0))
    row["volume"] = float(signal_data.get("volume", 0))
    row["spike"] = volume_map.get(row["symbol"], 0.0)
    row["call"], row["call_class"] = recommendation(row["score"], row["change"], row["spike"])
    row["confidence"] = confidence(row["score"], row["spike"], stats["winrate"])
    row["reason"] = short_reason(row["change"], row["spike"], row["score"])

top_pick = alpha_rows[0] if alpha_rows else None

# -------------------------
# HEADER
# -------------------------
col_left, col_right = st.columns([4, 1])

with col_left:
    st.markdown('<div class="hero-title">🛸 UFO Crypto Radar</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-sub">Personal operator dashboard for setups, heat, sandbox trades, and model tracking.</div>', unsafe_allow_html=True)

with col_right:
    if st.button("Refresh Radar", use_container_width=True):
        run_command(["python", "scanner.py"])
        run_command(["python", "signal_engine.py"])
        run_command(["python", "paper_trader.py"])
        st.rerun()

st.markdown('<div class="divider-space"></div>', unsafe_allow_html=True)

# -------------------------
# HERO CARD
# -------------------------
if top_pick:
    st.markdown('<div class="hero">', unsafe_allow_html=True)
    top1, top2 = st.columns([2.8, 2.2])

    with top1:
        st.markdown("### Best Setup Right Now")
        st.markdown(f"<div class='symbol-big'>{top_pick['symbol']}</div>", unsafe_allow_html=True)
        st.markdown(
            f"<span class='{top_pick['call_class']}'>{top_pick['call']}</span> "
            f"&nbsp;&nbsp;<span class='pill-blue'>Confidence {top_pick['confidence']}%</span>",
            unsafe_allow_html=True
        )
        st.markdown(
            f"<div class='muted' style='margin-top:0.6rem;'>"
            f"{top_pick['reason'].capitalize()}."
            f"</div>",
            unsafe_allow_html=True
        )
        st.markdown(
            f"<div class='small-note' style='margin-top:0.55rem;'>"
            f"Starter size: {starter_size(top_pick['price'], 100)}"
            f"</div>",
            unsafe_allow_html=True
        )

    with top2:
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.markdown(
                f"<div class='mini-card'><div class='metric-label'>Price</div><div class='metric-value'>${top_pick['price']:.6f}</div></div>",
                unsafe_allow_html=True
            )
        with m2:
            st.markdown(
                f"<div class='mini-card'><div class='metric-label'>24h Move</div><div class='metric-value'>{top_pick['change']:.2f}%</div></div>",
                unsafe_allow_html=True
            )
        with m3:
            st.markdown(
                f"<div class='mini-card'><div class='metric-label'>Volume Heat</div><div class='metric-value'>{top_pick['spike']:.2f}x</div></div>",
                unsafe_allow_html=True
            )
        with m4:
            st.markdown(
                f"<div class='mini-card'><div class='metric-label'>Score</div><div class='metric-value'>{top_pick['score']:.2f}</div></div>",
                unsafe_allow_html=True
            )
    st.markdown("</div>", unsafe_allow_html=True)

# -------------------------
# TABS
# -------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Assistant",
    "Radar",
    "Volume Heat",
    "Trades",
    "Model"
])

# -------------------------
# ASSISTANT TAB
# -------------------------
with tab1:
    st.subheader("Assistant Brief")
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.text(agent_output)
    st.markdown('</div>', unsafe_allow_html=True)

# -------------------------
# RADAR TAB
# -------------------------
with tab2:
    st.subheader("Top Setups")

    if not alpha_rows:
        st.write("No setups available yet.")
    else:
        for row in alpha_rows[:10]:
            st.markdown('<div class="top-setup-card">', unsafe_allow_html=True)
            c1, c2, c3 = st.columns([4, 2, 1])

            with c1:
                st.markdown(f"**{row['symbol']}**")
                st.markdown(
                    f"<span class='{row['call_class']}'>{row['call']}</span> "
                    f"<span class='pill-blue'>Confidence {row['confidence']}%</span>",
                    unsafe_allow_html=True
                )
                st.markdown(
                    f"<div class='muted'>"
                    f"Price ${row['price']:.6f} · "
                    f"24h {row['change']:.2f}% · "
                    f"Heat {row['spike']:.2f}x · "
                    f"{row['reason']}"
                    f"</div>",
                    unsafe_allow_html=True
                )

            with c2:
                st.write(f"**Score:** {row['score']:.2f}")
                st.write(f"**Starter:** {starter_size(row['price'], 100)}")

            with c3:
                if st.button("Analyze", key=f"analyze_{row['symbol']}"):
                    st.session_state["selected_symbol"] = row["symbol"]

            st.markdown('</div>', unsafe_allow_html=True)

        selected = st.session_state.get("selected_symbol")
        if selected:
            st.markdown("### Deep Analysis")
            deep_output = run_command(["python", "deep_scan.py", selected])
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.text(deep_output)
            st.markdown('</div>', unsafe_allow_html=True)

# -------------------------
# VOLUME TAB
# -------------------------
with tab3:
    st.subheader("Volume Heat")

    if volume_rows:
        for row in volume_rows[:10]:
            symbol = row["symbol"]
            spike = row["spike"]

            if spike >= 1.8:
                cls = "pill-green"
                label = "HOT"
            elif spike >= 1.2:
                cls = "pill-yellow"
                label = "WARM"
            else:
                cls = "pill-red"
                label = "COLD"

            st.markdown(
                f"<div class='section-card'><b>{symbol}</b> "
                f"<span class='{cls}'>{label}</span>"
                f"<div class='muted'>Current 5m volume is running at <b>{spike:.2f}x</b> recent average.</div>"
                f"</div>",
                unsafe_allow_html=True
            )
    else:
        st.write("No meaningful volume heat right now.")

# -------------------------
# TRADES TAB
# -------------------------
with tab4:
    st.subheader("Paper Trades")

    if st.button("Run Paper Trader"):
        run_command(["python", "paper_trader.py"])
        st.rerun()

    open_trades = [t for t in trade_log if t.get("status") == "OPEN"]
    closed_trades = [t for t in trade_log if t.get("status") != "OPEN"]

    st.markdown("#### Open")
    if open_trades:
        for trade in open_trades[-10:]:
            st.markdown(
                f"<div class='section-card'><b>{trade.get('symbol')}</b>"
                f"<div class='muted'>Entry: {trade.get('entry_price')} · Size: ${trade.get('size')} · Status: {trade.get('status')}</div>"
                f"</div>",
                unsafe_allow_html=True
            )
    else:
        st.write("No open trades.")

    st.markdown("#### Closed")
    if closed_trades:
        for trade in closed_trades[-10:]:
            status = trade.get("status", "N/A")
            cls = "pill-green" if status == "WIN" else "pill-red"
            st.markdown(
                f"<div class='section-card'><b>{trade.get('symbol')}</b> "
                f"<span class='{cls}'>{status}</span>"
                f"<div class='muted'>Entry: {trade.get('entry_price')} · Exit: {trade.get('exit_price', '-')}</div>"
                f"</div>",
                unsafe_allow_html=True
            )
    else:
        st.write("No closed trades yet.")

# -------------------------
# MODEL TAB
# -------------------------
with tab5:
    st.subheader("Model Performance")

    a, b, c, d = st.columns(4)
    with a:
        st.markdown(
            f"<div class='mini-card'><div class='metric-label'>Trades</div><div class='metric-value'>{stats['total']}</div></div>",
            unsafe_allow_html=True
        )
    with b:
        st.markdown(
            f"<div class='mini-card'><div class='metric-label'>Wins</div><div class='metric-value'>{stats['wins']}</div></div>",
            unsafe_allow_html=True
        )
    with c:
        st.markdown(
            f"<div class='mini-card'><div class='metric-label'>Losses</div><div class='metric-value'>{stats['losses']}</div></div>",
            unsafe_allow_html=True
        )
    with d:
        st.markdown(
            f"<div class='mini-card'><div class='metric-label'>Win Rate</div><div class='metric-value'>{stats['winrate']:.2f}%</div></div>",
            unsafe_allow_html=True
        )

    st.markdown('<div class="divider-space"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.text(stats_output)
    st.markdown('</div>', unsafe_allow_html=True)
